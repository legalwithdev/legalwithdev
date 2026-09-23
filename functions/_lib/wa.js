// functions/_lib/wa.js - WhatsApp shared helpers (constants, memory, rate-limit, diagnostics, send)
// _lib me isliye taaki Cloudflare route na bane (underscore = routing se bahar).
// DIAGNOSTICS: KV me sirf counts/status likhe jaate hain - user ka content NAHI.

export const GRAPH_VERSION = "v21.0";
export const RATE_LIMIT_CHAT = 20; // messages per hour, per user
export const MAX_TURNS = 12; // context messages per user (6 user + 6 bot)
export const MEMORY_TTL = 7 * 24 * 3600; // 7 din
export const CHUNK_CHAR_LIMIT = 3900; // WhatsApp 4096 char limit, safe margin
const DIAG_TTL = 3 * 24 * 3600; // diagnostics 3 din

export const RATE_LIMIT_REPLY =
  "Aap bahut zyada messages bhej rahe hain. Thoda ruk kar phir try karein (1 ghante me limited sawal allowed hain).\n" +
  "आप बहुत ज़्यादा संदेश भेज रहे हैं। थोड़ा रुककर फिर प्रयास करें।\n" +
  "You are sending too many messages. Please wait a while and try again.\n\n" +
  "Yeh free service hai - sab users ke liye available rakhne ke liye limit hai. NALSA: nalsa.gov.in / 15100.";

export const BOT_DISCLOSURE =
  "🤖 Ye ek automated legal-information assistant hai (LegalWithDev).\n" +
  "🤖 यह एक स्वचालित कानूनी जानकारी सहायक है (LegalWithDev)।\n" +
  "🤖 This is an automated legal-information assistant (LegalWithDev).\n\n";

export const ATTACHMENT_REPLY =
  "Main abhi sirf TEXT messages samajh sakta hoon - apna sawal likh kar bhejein.\n" +
  "मैं अभी केवल टेक्स्ट संदेश समझ सकता हूँ - अपना प्रश्न लिखकर भेजें।\n" +
  "I can only understand TEXT messages for now - please type your question";

// ---------- rate limiting (in-memory, approximate) ---------- //
const buckets = new Map();
export function rateLimited(key, limit) {
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
export async function loadHistory(env, key) {
  if (env.LWD_KV) {
    try {
      const raw = await env.LWD_KV.get(key);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* fall through */ }
  }
  return memFallback.get(key) || [];
}
export async function saveHistory(env, key, history) {
  if (env.LWD_KV) {
    try {
      await env.LWD_KV.put(key, JSON.stringify(history), { expirationTtl: MEMORY_TTL });
      return;
    } catch (e) { /* fall through */ }
  }
  memFallback.set(key, history);
}

// pehli baar disclosure bheja? (Meta policy: bot hone ka pata chalna chahiie)
export async function needsDisclosure(env, waId) {
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

// ---------- diagnostics (flight recorder - receipts ke liye) ---------- //
export async function recordDiag(env, key, obj) {
  if (!env.LWD_KV) return;
  try {
    await env.LWD_KV.put(key, JSON.stringify(obj), { expirationTtl: DIAG_TTL });
  } catch (e) { /* ignore */ }
}
export async function bumpDiagCount(env) {
  if (!env.LWD_KV) return;
  try {
    const c = Number((await env.LWD_KV.get("wa:diag:count")) || "0") + 1;
    await env.LWD_KV.put("wa:diag:count", String(c), { expirationTtl: DIAG_TTL });
  } catch (e) { /* ignore */ }
}

// ---------- WhatsApp Send API (Cloud API, free) ---------- //
export async function sendWAMessage(token, phoneId, to, text) {
  if (!token || !phoneId) return { status: 0, body: "missing-token-or-phone-id" };
  try {
    const res = await fetch(`https://graph.facebook.com/${GRAPH_VERSION}/${phoneId}/messages`, {
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
    const body = await res.text().catch(() => "");
    return { status: res.status, body: body.slice(0, 300) };
  } catch (e) {
    return { status: -1, body: String((e && e.message) || e).slice(0, 300) };
  }
}

// WhatsApp limit ke andar chunks (characters me)
export function chunkByChars(text, limit) {
  const chunks = [];
  for (let i = 0; i < text.length; i += limit) {
    chunks.push(text.slice(i, i + limit));
  }
  return chunks;
}

// ---------- webhook signature verify (optional, agar WHATSAPP_APP_SECRET set hai) ---------- //
export async function validSignature(request, rawBody, appSecret) {
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
