#!/usr/bin/env python3
# Step 2: add server-side YouTube proxy (functions/api/videos.js) and wire the
# video overlay to fetch /api/videos. Key stays in env (never in the browser).
import os

FUNCTION_JS = '''// functions/api/videos.js  ->  GET /api/videos
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
'''

OLD_SCRIPT = """  <script>
  (function(){
    var b=document.getElementById('vidBtn'), o=document.getElementById('vidOver'), c=document.getElementById('vidClose');
    if(b&&o) b.addEventListener('click',function(){ o.classList.add('on'); });
    if(c&&o) c.addEventListener('click',function(){ o.classList.remove('on'); });
    if(o) o.addEventListener('click',function(e){ if(e.target===o) o.classList.remove('on'); });
  })();
  </script>"""

NEW_SCRIPT = """  <script>
  (function(){
    var b=document.getElementById('vidBtn'), o=document.getElementById('vidOver'), c=document.getElementById('vidClose');
    if(!o) return;
    var loaded=false;
    function open(){ o.classList.add('on'); if(!loaded){ loaded=true; load(); } }
    function close(){ o.classList.remove('on'); }
    if(b) b.addEventListener('click', open);
    if(c) c.addEventListener('click', close);
    o.addEventListener('click', function(e){ if(e.target===o) close(); });
    function esc(s){ return String(s||'').replace(/[&<>"]/g, function(m){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]; }); }
    function load(){
      var panel=o.querySelector('.vidpanel'); if(!panel) return;
      var box=document.createElement('div'); box.className='vidbody';
      box.innerHTML='<p class="vidempty">Loading videos...</p>';
      panel.appendChild(box);
      fetch('/api/videos').then(function(r){ return r.json(); }).then(function(d){
        var vids=(d&&d.videos)||[];
        if(!vids.length){
          box.innerHTML='<p class="vidempty">Legal explainer videos will appear here soon. This is general information, not legal advice.</p>';
          return;
        }
        var player=document.createElement('div'); player.className='vidplayer';
        function play(v){
          player.innerHTML='<iframe src="https://www.youtube.com/embed/'+encodeURIComponent(v.id)+'" title="'+esc(v.title)+'" loading="lazy" allowfullscreen allow="accelerometer; encrypted-media; picture-in-picture"></iframe>';
        }
        var list=document.createElement('div'); list.className='vidlist';
        vids.forEach(function(v){
          var it=document.createElement('button'); it.type='button'; it.className='vitem';
          it.innerHTML='<span class="vt">'+esc(v.title)+'</span>'+(v.channel?'<span class="vd">'+esc(v.channel)+'</span>':'');
          it.addEventListener('click', function(){ play(v); });
          list.appendChild(it);
        });
        box.innerHTML=''; box.appendChild(player); box.appendChild(list);
        play(vids[0]);
      }).catch(function(){
        box.innerHTML='<p class="vidempty">Videos could not be loaded. Please check your internet connection.</p>';
      });
    }
  })();
  </script>"""

CSS2 = """
  .vidbody{margin-top:2px}
  .vidplayer iframe{display:block;width:100%;aspect-ratio:16/9;border:0;border-radius:12px}
  .vidlist{display:flex;flex-direction:column;gap:8px;margin-top:12px;max-height:36vh;overflow:auto}
  .vitem{display:flex;flex-direction:column;gap:2px;text-align:left;cursor:pointer;border-radius:10px;padding:10px 12px;border:1px solid rgba(128,128,128,.3);background:transparent;color:inherit;font-family:inherit}
  .vitem:hover{border-color:rgba(128,128,128,.6)}
  .vitem .vt{font-size:13.5px;font-weight:600}
  .vitem .vd{font-size:11.5px;opacity:.7}
</style>"""

os.makedirs('functions/api', exist_ok=True)
open('functions/api/videos.js', 'w', encoding='utf-8').write(FUNCTION_JS)
print('WROTE functions/api/videos.js')

for p in ['index.html', 'app.html']:
    s = open(p, encoding='utf-8').read()
    if 'fetch(\'/api/videos\')' in s:
        print('SKIP already wired:', p); continue
    assert OLD_SCRIPT in s, 'old overlay script not found in ' + p
    s = s.replace(OLD_SCRIPT, NEW_SCRIPT, 1)
    s = s.replace('</style>', CSS2, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('WIRED', p)

print('DONE')
