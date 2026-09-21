// functions/webhook/instagram.js - POST+GET /webhook/instagram (Instagram DM bot, Pages Function)
// Telegram wale pattern par based: same brain (Gemini), same memory (KV warna in-memory).
// Meta rule: automated bot ko pehli baar batana hota hai ki ye automated hai - DISCLOSURE line.

import { createBrain } from "../_lib/brain.js";

const GRAPH_VERSION = "v21.0";
const RATE_LIMIT_CHAT = 20; // messages per hour, per DM user
const MAX_TURNS = 12; // messages of context per user (6 user + 6 bot)
const MEMORY_TTL = 7 * 24 * 3600; // 7 din
const IG_MSG_BYTE_LIMIT = 1000; // Meta hard limit per message (UTF-8 bytes)
const CHUNK_BYTE_LIMIT = 900; // safe margin

const RATE_LIMIT_REPLY =
  "Aap bahut zyada messages bhej rahe hain. Thoda ruk kar phir try karein (1 ghante me limited sawal allowed hain).\n" +
  "आप बहुत ज़्यादा संदेश भेज रहे हैं। थोड़ा रुककर फिर प्रयास करें।\n" +
  "You are sending too many messages. Please wait a while and try again.\n\n" +
  "Yeh free service hai - sab users ke liye available rakhne ke liye limit hai. NALSA: nalsa.gov.in / 15100.";

const BOT_DISCLOSURE =
  "🤖 Ye ek automated legal-information assistant hai (LegalWithDev).\n" +
  "🤖 यह एक स्वचालित कानूनी जानकारी सहायक है (LegalWithDev)।\n" +
  "🤖 This is an automated legal-information assistant (LegalWithDev).\n\n";

const ATTACHMENT_REPLY =
  "Main abhi sirf TEXT messages samajh sakta hoon - apna sawal likh kar bhejein.\n" +
  "मैं अभी केवल टेक्स्ट संदेश समझ सकता हूँ - अपना प्रश्न लिखकर भेजें।\n" +
  "I can only understand TEXT messages for now - please type your question.\n\n" +
  DISCLAIMER_LINE();

function DISCLAIMER_LINE() {
  return "Kanooni salah ke liye qualified Advocate/Lawyer se milein. NALSA: nalsa.gov.in / 15100.";
}

// ---------- rate limiting (in-memory, approximate) ---------- //
const buckets = new Map();
function rateLimited(key, limit) {
  const now = Date.now();
  const hits = (buckets.get(key) || []).filter((t) => now - t < 3600000);
  if (hits.length >= limit) {
    buckets.set(key, hits);
    return true;
  }
  hits.push(now);
  buckets.set(key, hits);
  return false;
}

// ---------- conversation memory: KV (reliable) + fallback in-memory ---------- //
const memFallback = new Map();
async function loadHistory(env, key) {
  if (env.LWD_KV) {
    try {
      const raw = await env.LWD_KV.get(key);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* fall through */ }
  }
  return memFallback.get(key) || [];
}
async function saveHistory(env, key, history) {
  if (env.LWD_KV) {
    try {
      await env.LWD_KV.put(key, JSON.stringify(history), { expirationTtl: MEMORY_TTL });
      return;
    } catch (e) { /* fall through */ }
  }
  memFallback.set(key, history);
}

// pehli baar disclosure bheja? (Meta policy: bot hone ka pata chalna chahiye)
async function needsDisclosure(env, igsid) {
  const key = "ig:greeted:" + igsid;
  if (env.LWD_KV) {
    try {
      const raw = await env.LWD_KV.get(key);
      if (raw) return false;
      await env.LWD_KV.put(key, "1", { expirationTtl: 90 * 24 * 3600 });
    } catch (e) { /* fall through */ }
  } else {
    if (memFallback.has(key)) return false;
    memFallback.set(key, "1");
  }
  return true;
}

// ---------- Instagram Send API ---------- //
async function sendIGMessage(pat, igsid, text) {
  if (!pat) return;
  try {
    await fetch(`https://graph.facebook.com/${GRAPH_VERSION}/me/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        recipient: { id: igsid },
        message: { text },
      }),
    });
  } catch (e) {
    /* ek reply fail ho jaye to bot crash nahi hota */
  }
}

// 1000-byte limit ke andar UTF-8 chunks (Devanagari 3 bytes/char hoti hai)
function chunkByBytes(text, limit) {
  const chunks = [];
  let cur = "";
  let curBytes = 0;
  for (const ch of text) {
    const chBytes = new TextEncoder().encode(ch).length;
    if (curBytes + chBytes > limit) {
      if (cur) chunks.push(cur);
      cur = ch;
      curBytes = chBytes;
    } else {
      cur += ch;
      curBytes += chBytes;
    }
  }
  if (cur) chunks.push(cur);
  return chunks;
}

// ---------- webhook signature verify (optional, agar IG_APP_SECRET set hai) ---------- //
async function validSignature(request, rawBody, appSecret) {
  if (!appSecret) return true; // secret set nahi hai to skip (deploy aasan)
  const sigHeader = request.headers.get("X-Hub-Signature-256") || "";
  if (!sigHeader.startsWith("sha256=")) return false;
  const expected = sigHeader.slice(7);
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(appSecret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(rawBody));
  const hex = [...new Uint8Array(mac)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return hex === expected;
}

// ---------- GET: Meta webhook verification handshake ---------- //
export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const mode = url.searchParams.get("hub.mode");
  const token = url.searchParams.get("hub.verify_token");
  const challenge = url.searchParams.get("hub.challenge");
  if (mode === "subscribe" && token && token === (env.IG_VERIFY_TOKEN || "")) {
    return new Response(challenge || "", { status: 200 });
  }
  return new Response("Forbidden", { status: 403 });
}

// ---------- POST: DM aayi -> jawab do ---------- //
export async function onRequestPost(context) {
  const { request, env } = context;
  const pat = env.IG_PAGE_ACCESS_TOKEN || "";
  const brain = createBrain(env);

  const rawBody = await request.text();
  if (!(await validSignature(request, rawBody, env.IG_APP_SECRET || ""))) {
    return new Response("Forbidden", { status: 403 });
  }

  let payload = {};
  try {
    payload = JSON.parse(rawBody);
  } catch (e) {
    return Response.json({ ok: true });
  }

  const entries = payload.entry || [];
  for (const entry of entries) {
    const messagings = entry.messaging || [];
    for (const m of messagings) {
      const msg = m.message || {};
      if (msg.is_echo) continue; // hamara apna bheja hua message
      if (msg.is_deleted) continue; // user ne delete kiya
      if (msg.is_unsupported) continue;

      const igsid = m.sender && m.sender.id;
      if (!igsid) continue;

      const text = String(msg.text || "").trim();

      if (!text) {
        // story reply/attachment - abhi text hi chalta hai
        if (msg.attachments || msg.reply_to || msg.sticker_id) {
          await sendIGMessage(pat, igsid, ATTACHMENT_REPLY);
        }
        continue;
      }

      if (rateLimited("ig:" + igsid, RATE_LIMIT_CHAT)) {
        await sendIGMessage(pat, igsid, RATE_LIMIT_REPLY);
        continue;
      }

      const memKey = "ig:" + igsid;
      const history = await loadHistory(env, memKey);
      let reply = await brain.reply(text, history, "");

      if (await needsDisclosure(env, igsid)) {
        reply = BOT_DISCLOSURE + reply;
      }

      history.push({ role: "user", content: text });
      history.push({ role: "assistant", content: reply.slice(0, 700) });
      await saveHistory(env, memKey, history.slice(-MAX_TURNS));

      for (const chunk of chunkByBytes(reply, CHUNK_BYTE_LIMIT)) {
        await sendIGMessage(pat, igsid, chunk);
      }
    }
  }
  return Response.json({ ok: true });
}
