// functions/webhook/whatsapp.js - POST+GET /webhook/whatsapp (WhatsApp bot, Pages Function)
// Instagram/Telegram wale pattern par based: same brain (Gemini), same memory (KV warna in-memory).
// WhatsApp Cloud API (Meta ka FREE tier) - koi Twilio/ paisa nahi.
// Meta rule: automated bot ko pehli baar batana hota hai ki ye automated hai - DISCLOSURE line.

import { createBrain } from "../_lib/brain.js";

const GRAPH_VERSION = "v21.0";
const RATE_LIMIT_CHAT = 20; // messages per hour, per user
const MAX_TURNS = 12; // messages of context per user (6 user + 6 bot)
const MEMORY_TTL = 7 * 24 * 3600; // 7 din
const WA_MSG_CHAR_LIMIT = 4096; // WhatsApp text message hard limit (characters)
const CHUNK_CHAR_LIMIT = 3900; // safe margin

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
  "I can only understand TEXT messages for now - please type your question.";

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
async function needsDisclosure(env, waId) {
  const key = "wa:greeted:" + waId;
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

// ---------- WhatsApp Send API (Cloud API, free) ---------- //
async function sendWAMessage(token, phoneId, to, text) {
  if (!token || !phoneId) return;
  try {
    await fetch(`https://graph.facebook.com/${GRAPH_VERSION}/${phoneId}/messages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        messaging_product: "whatsapp",
        recipient_type: "individual",
        to,
        type: "text",
        text: { body: text, preview_url: false },
      }),
    });
  } catch (e) {
    /* ek reply fail ho jaye to bot crash nahi hota */
  }
}

// WhatsApp limit ke andar chunks (4096 chars, characters me - bytes me nahi)
function chunkByChars(text, limit) {
  const chunks = [];
  for (let i = 0; i < text.length; i += limit) {
    chunks.push(text.slice(i, i + limit));
  }
  return chunks;
}

// ---------- webhook signature verify (optional, agar WHATSAPP_APP_SECRET set hai) ---------- //
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
  if (mode === "subscribe" && token && token === (env.WHATSAPP_VERIFY_TOKEN || "")) {
    return new Response(challenge || "", { status: 200 });
  }
  return new Response("Forbidden", { status: 403 });
}

// ---------- POST: message aaya -> jawab do ---------- //
export async function onRequestPost(context) {
  const { request, env } = context;
  const token = env.WHATSAPP_TOKEN || "";
  const brain = createBrain(env);

  const rawBody = await request.text();
  if (!(await validSignature(request, rawBody, env.WHATSAPP_APP_SECRET || ""))) {
    return new Response("Forbidden", { status: 403 });
  }

  let payload = {};
  try {
    payload = JSON.parse(rawBody);
  } catch (e) {
    return Response.json({ ok: true });
  }
  if (payload.object !== "whatsapp_business_account") {
    return Response.json({ ok: true });
  }

  const entries = payload.entry || [];
  for (const entry of entries) {
    const changes = entry.changes || [];
    for (const change of changes) {
      const value = (change && change.value) || {};
      if (value.statuses && value.statuses.length) continue; // delivery/read receipts - ignore

      const phoneId =
        (value.metadata && value.metadata.phone_number_id) ||
        env.WHATSAPP_PHONE_ID ||
        "";
      const messages = value.messages || [];
      for (const msg of messages) {
        const from = msg.from; // WhatsApp user ka number (wa_id)
        if (!from) continue;

        const text = String((msg.text && msg.text.body) || "").trim();
        if (!text) {
          // image/audio/document/video/sticker - abhi text hi chalta hai
          if (msg.type && msg.type !== "text") {
            await sendWAMessage(token, phoneId, from, ATTACHMENT_REPLY);
          }
          continue;
        }

        if (rateLimited("wa:" + from, RATE_LIMIT_CHAT)) {
          await sendWAMessage(token, phoneId, from, RATE_LIMIT_REPLY);
          continue;
        }

        const memKey = "wa:" + from;
        const history = await loadHistory(env, memKey);
        let reply = await brain.reply(text, history, "");

        if (await needsDisclosure(env, from)) {
          reply = BOT_DISCLOSURE + reply;
        }

        history.push({ role: "user", content: text });
        history.push({ role: "assistant", content: reply.slice(0, 700) });
        await saveHistory(env, memKey, history.slice(-MAX_TURNS));

        for (const chunk of chunkByChars(reply, CHUNK_CHAR_LIMIT)) {
          await sendWAMessage(token, phoneId, from, chunk);
        }
      }
    }
  }
  return Response.json({ ok: true });
}
