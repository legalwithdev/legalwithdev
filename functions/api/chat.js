// functions/api/chat.js - POST /api/chat (web chat, Pages Function)
// Ab yahi Render wale /api/chat ka kaam karta hai - Cloudflare pe (kabhi nahi sota).

import { createBrain } from "../_lib/brain.js";

const RATE_LIMIT_WEB = 15; // messages per hour, per visitor
const RATE_LIMIT_REPLY =
  "Aap bahut zyada messages bhej rahe hain. Thoda ruk kar phir try karein (1 ghante me limited sawal allowed hain).\n" +
  "आप बहुत ज़्यादा संदेश भेज रहे हैं। थोड़ा रुककर फिर प्रयास करें।\n" +
  "You are sending too many messages. Please wait a while and try again.\n\n" +
  "Yeh free service hai - sab users ke liye available rakhne ke liye limit hai. NALSA: nalsa.gov.in / 15100.";

// In-memory rate limiting (approximate - Workers me isolate badal sakta hai,
// par abuse rokn ke liye kaafi hai; KV use nahi kiya - writes ki limit bachane ke liye)
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

export async function onRequestPost(context) {
  const { request, env } = context;
  let payload = {};
  try {
    payload = await request.json();
  } catch (e) {
    payload = {};
  }
  const ip = request.headers.get("CF-Connecting-IP") || (request.headers.get("X-Forwarded-For") || "unknown").split(",")[0].trim();
  if (rateLimited("web:" + ip, RATE_LIMIT_WEB)) {
    return Response.json({ reply: RATE_LIMIT_REPLY });
  }
  const brain = createBrain(env);
  const reply = await brain.reply(payload.message, payload.history || [], payload.language || "");
  return Response.json({ reply });
}
