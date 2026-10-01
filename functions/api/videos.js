// functions/api/videos.js  ->  GET /api/videos
// Server-side proxy for YouTube Data API v3. The API key stays in the Cloudflare
// env (YT_API_KEY) and is NEVER sent to the browser.
// Configure ONE source (Cloudflare Pages > Settings > Environment variables):
//   YT_API_KEY  : your YouTube Data API v3 key            (required)
//   YT_CHANNELS : comma-separated YouTube channel IDs      (preferred, curated)
//   YT_QUERY    : a search phrase (used if no channels set)
const API = "https://www.googleapis.com/youtube/v3";
const MAX = 12;

function j(obj) {
  return new Response(JSON.stringify(obj), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=600",
    },
  });
}
async function gj(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error("yt " + r.status);
  return r.json();
}
async function fromChannel(id, key) {
  const c = await gj(`${API}/channels?part=contentDetails&id=${encodeURIComponent(id)}&key=${key}`);
  const up = c.items && c.items[0] && c.items[0].contentDetails &&
             c.items[0].contentDetails.relatedPlaylists &&
             c.items[0].contentDetails.relatedPlaylists.uploads;
  if (!up) return [];
  const p = await gj(`${API}/playlistItems?part=snippet&maxResults=${MAX}&playlistId=${up}&key=${key}`);
  return (p.items || []).map((it) => ({
    id: it.snippet && it.snippet.resourceId && it.snippet.resourceId.videoId,
    title: it.snippet && it.snippet.title,
    channel: it.snippet && it.snippet.channelTitle,
  })).filter((v) => v.id);
}
async function fromSearch(q, key) {
  const s = await gj(`${API}/search?part=snippet&type=video&maxResults=${MAX}&q=${encodeURIComponent(q)}&key=${key}`);
  return (s.items || []).map((it) => ({
    id: it.id && it.id.videoId,
    title: it.snippet && it.snippet.title,
    channel: it.snippet && it.snippet.channelTitle,
  })).filter((v) => v.id);
}
export async function onRequestGet(context) {
  const env = (context && context.env) || {};
  const key = (env.YT_API_KEY || "").trim();
  if (!key) return j({ videos: [], note: "not_configured" });
  const channels = (env.YT_CHANNELS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const query = (env.YT_QUERY || "").trim();
  try {
    let videos = [];
    if (channels.length) {
      const lists = await Promise.all(channels.slice(0, 4).map((c) => fromChannel(c, key).catch(() => [])));
      videos = lists.flat().slice(0, MAX);
    } else if (query) {
      videos = await fromSearch(query, key);
    } else {
      return j({ videos: [], note: "no_source" });
    }
    return j({ videos });
  } catch (e) {
    return j({ videos: [], note: "fetch_error" });
  }
}
