// functions/webhook/telegram.js - POST /webhook/telegram (Telegram bot, Pages Function)
// Render wale Telegram webhook ka kaam - ab Cloudflare pe. Kabhi nahi sota.
// Memory: KV (agar LWD_KV binding hai) warna in-memory (approximate).

import { createBrain } from "../_lib/brain.js";

const RATE_LIMIT_CHAT = 20; // messages per hour, per chat
const MAX_TURNS = 12; // messages of context per chat (6 user + 6 bot)
const MEMORY_TTL = 7 * 24 * 3600; // 7 din baad purani history khud khatam

const RATE_LIMIT_REPLY =
  "Aap bahut zyada messages bhej rahe hain. Thoda ruk kar phir try karein (1 ghante me limited sawal allowed hain).\n" +
  "आप बहुत ज़्यादा संदेश भेज रहे हैं। थोड़ा रुककर फिर प्रयास करें।\n" +
  "You are sending too many messages. Please wait a while and try again.\n\n" +
  "Yeh free service hai - sab users ke liye available rakhne ke liye limit hai. NALSA: nalsa.gov.in / 15100.";

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

async function sendTelegramMessage(token, chatId, text) {
  if (!token) return;
  try {
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, text }),
    });
  } catch (e) {
    /* ek reply fail ho jaye to bot crash nahi hota */
  }
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const token = env.TELEGRAM_BOT_TOKEN || "";
  const brain = createBrain(env);

  let update = {};
  try {
    update = await request.json();
  } catch (e) {
    return Response.json({ ok: true });
  }
  const message = update.message || update.edited_message || {};
  const chatId = message.chat && message.chat.id;
  const text = String(message.text || "").trim();
  if (!chatId) return Response.json({ ok: true });

  const about =
    "LegalWithDev - Indian legal information assistant for Bharat.\n\n" +
    "Poochho kuch bhi: consumer rights, tenant/rent issues, divorce & maintenance, " +
    "salary disputes, FIR & police matters, cheque bounce, RTI, property, ragging, " +
    "online fraud (UPI scams), aur free legal aid.\n\n" +
    "Answers in your native language + Hindi + English.\n\n" + brain.disclaimer;

  if (text.startsWith("/start") || text.startsWith("/help")) {
    await sendTelegramMessage(token, chatId, about);
  } else if (text) {
    if (rateLimited("tg:" + chatId, RATE_LIMIT_CHAT)) {
      await sendTelegramMessage(token, chatId, RATE_LIMIT_REPLY);
      return Response.json({ ok: true });
    }
    const memKey = "tg:" + chatId;
    const history = await loadHistory(env, memKey);
    const reply = await brain.reply(text, history, "");
    // nayi history save karo (user + bot, bot reply 700 chars tak)
    history.push({ role: "user", content: text });
    history.push({ role: "assistant", content: reply.slice(0, 700) });
    await saveHistory(env, memKey, history.slice(-MAX_TURNS));
    // Telegram 4096 chars limit - tukdon me bhejo
    for (let i = 0; i < reply.length; i += 4096) {
      await sendTelegramMessage(token, chatId, reply.slice(i, i + 4096));
    }
  }
  return Response.json({ ok: true });
}
