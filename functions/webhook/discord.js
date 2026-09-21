// functions/webhook/discord.js - POST+GET /webhook/discord (Discord bot, Pages Function)
// Discord ka alag model: bot DM nahi karta, slash command hota hai "/ask".
// Rule: Discord ko 3 second me jawab dena hota hai, isliye pehle "typing..."
// bhejte hain (type 5), phir Gemini ka jawab aane pe message edit karte hain.

import { createBrain } from "../_lib/brain.js";

const DISCORD_API = "https://discord.com/api/v10";
const RATE_LIMIT_CHAT = 20; // commands per hour, per user
const MAX_TURNS = 12; // messages of context per user (6 user + 6 bot)
const MEMORY_TTL = 7 * 24 * 3600; // 7 din
const MSG_MAX_CHARS = 1900; // Discord limit 2000 chars
const MSG_MAX_BYTES = 5500; // safe UTF-8 margin

const RATE_LIMIT_REPLY =
  "Aap bahut zyada commands use kar rahe hain. Thoda ruk kar phir try karein (1 ghante me limited sawal allowed hain).\n" +
  "आप बहुत ज़्यादा commands use कर रहे हैं। थोड़ा रुककर फिर प्रयास करें।\n" +
  "You are using too many commands. Please wait a while and try again.\n\n" +
  "Yeh free service hai - sab users ke liye available rakhne ke liye limit hai. NALSA: nalsa.gov.in / 15100.";

const BOT_DISCLOSURE =
  "🤖 Ye ek automated legal-information assistant hai (LegalWithDev).\n\n";

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

// pehli baar disclosure bheja? (bot hone ka pata chalna chahiye)
async function needsDisclosure(env, uid) {
  const key = "dc:greeted:" + uid;
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

// char AUR byte dono limit ke andar chunks
function chunkMessage(text) {
  const chunks = [];
  let cur = "";
  let curBytes = 0;
  for (const ch of text) {
    const chBytes = new TextEncoder().encode(ch).length;
    const nextLen = cur.length + 1;
    const nextBytes = curBytes + chBytes;
    if (nextLen > MSG_MAX_CHARS || nextBytes > MSG_MAX_BYTES) {
      if (cur) chunks.push(cur);
      cur = ch;
      curBytes = chBytes;
    } else {
      cur += ch;
      curBytes = nextBytes;
    }
  }
  if (cur) chunks.push(cur);
  return chunks;
}

function hexToBytes(hex) {
  const clean = String(hex || "").replace(/[^0-9a-fA-F]/g, "");
  const out = new Uint8Array(clean.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(clean.substr(i * 2, 2), 16);
  return out;
}

// ---------- Discord Ed25519 signature verify (COMPULSORY - yahi auth hai) ---------- //
async function validSignature(request, rawBody, publicKeyHex) {
  if (!publicKeyHex) return false; // key set nahi = request reject
  const sigHex = request.headers.get("X-Signature-Ed25519") || "";
  const timestamp = request.headers.get("X-Signature-Timestamp") || "";
  if (!sigHex || !timestamp) return false;
  let sig = hexToBytes(sigHex);
  if (sig.length === 65 && sig[0] === 0x30) sig = sig.slice(1); // leading 0x30 hatao
  const key = await crypto.subtle.importKey("raw", hexToBytes(publicKeyHex), { name: "Ed25519" }, false, ["verify"]);
  const data = new TextEncoder().encode(timestamp + rawBody);
  return await crypto.subtle.verify("Ed25519", key, sig, data);
}

// ---------- reply: pehle ack, phir edit ---------- //
async function sendDiscordReply(env, interaction, reply) {
  const appId = interaction.application_id;
  const token = interaction.token;
  if (!appId || !token) return;
  const chunks = chunkMessage(reply);
  try {
    // 1) original "typing..." message edit karo (pehla chunk)
    await fetch(`${DISCORD_API}/webhooks/${appId}/${token}/messages/@original`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: chunks[0] || "..." }),
    });
    // 2) bache hue chunks naye messages me
    for (const c of chunks.slice(1)) {
      await fetch(`${DISCORD_API}/webhooks/${appId}/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: c }),
      });
    }
  } catch (e) {
    /* ek reply fail ho jaye to bot crash nahi hota */
  }
}

async function handleAsk(env, interaction, brain) {
  const uid =
    (interaction.member && interaction.member.user && interaction.member.user.id) ||
    (interaction.user && interaction.user.id) ||
    "unknown";

  const options = (interaction.data && interaction.data.options) || [];
  const opt = options.find((o) => o.name === "sawal" || o.name === "question");
  const question = String((opt && opt.value) || "").trim();

  if (!question) {
    await sendDiscordReply(env, interaction, "Sawal likhna zaroori hai: `/ask sawal:your legal question`");
    return;
  }

  if (rateLimited("dc:" + uid, RATE_LIMIT_CHAT)) {
    await sendDiscordReply(env, interaction, RATE_LIMIT_REPLY);
    return;
  }

  const memKey = "dc:" + uid;
  const history = await loadHistory(env, memKey);
  let reply = await brain.reply(question, history, "");

  if (await needsDisclosure(env, uid)) {
    reply = BOT_DISCLOSURE + reply;
  }

  history.push({ role: "user", content: question });
  history.push({ role: "assistant", content: reply.slice(0, 700) });
  await saveHistory(env, memKey, history.slice(-MAX_TURNS));

  await sendDiscordReply(env, interaction, reply);
}

// ---------- GET: setup route - slash command register karo ---------- //
// /webhook/discord?setup=<DISCORD_ADMIN_KEY>  (browser me kholna hai EK baar)
export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const setupKey = url.searchParams.get("setup") || "";
  const adminKey = env.DISCORD_ADMIN_KEY || "";
  const appId = env.DISCORD_APP_ID || "";
  const botToken = env.DISCORD_BOT_TOKEN || "";
  if (!setupKey || !adminKey || setupKey !== adminKey) {
    return new Response("Forbidden", { status: 403 });
  }
  if (!appId || !botToken) {
    return Response.json({ ok: false, error: "DISCORD_APP_ID ya DISCORD_BOT_TOKEN env var set nahi hai" });
  }
  // /ask command register karta hai
  const body = {
    name: "ask",
    description: "Ask LegalWithDev any Indian legal question (multi-language)",
    options: [
      {
        type: 3, // STRING
        name: "sawal",
        description: "Your legal question (any Indian language or English)",
        required: true,
      },
    ],
  };
  try {
    const res = await fetch(`${DISCORD_API}/applications/${appId}/commands`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bot ${botToken}` },
      body: JSON.stringify(body),
    });
    const data = await res.text();
    return Response.json({ ok: res.ok, status: res.status, detail: data.slice(0, 500) });
  } catch (e) {
    return Response.json({ ok: false, error: String(e) });
  }
}

// ---------- POST: interaction aaya ---------- //
export async function onRequestPost(context) {
  const { request, env } = context;

  const rawBody = await request.text();
  if (!(await validSignature(request, rawBody, env.DISCORD_APP_PUBLIC_KEY || ""))) {
    return new Response("Invalid request signature", { status: 401 });
  }

  let interaction = {};
  try {
    interaction = JSON.parse(rawBody);
  } catch (e) {
    return new Response("Bad request", { status: 400 });
  }

  // PING: URL save karte waqt Discord ye bhejta hai
  if (interaction.type === 1) {
    return Response.json({ type: 1 });
  }

  // slash command
  if (interaction.type === 2) {
    if ((interaction.data && interaction.data.name) === "ask") {
      const brain = createBrain(env);
      // 3-second rule: turant "soch raha hoon..." bhejo (type 5 = deferred)
      const work = handleAsk(env, interaction, brain);
      if (context.waitUntil) context.waitUntil(work);
      return Response.json({ type: 5 });
    }
    return Response.json({ type: 4, data: { content: "Unknown command." } });
  }

  // autocomplete / buttons waghera - bas acknowledge
  if (interaction.type === 4) {
    return Response.json({ type: 8, data: { choices: [] } });
  }
  return Response.json({ type: 6 });
}
