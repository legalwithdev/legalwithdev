// functions/webhook/whatsapp.js - POST+GET /webhook/whatsapp (WhatsApp bot, Pages Function)
// Handlers only - helpers functions/_lib/wa.js me.
// FIX: Meta ko TURANT 200 do (waitUntil me background process) - duplicate replies ka ilaaj.
// FIX: message-ID dedup (Meta retry aaye to bhi ek hi reply).

import { createBrain } from "../_lib/brain.js";
import {
  RATE_LIMIT_CHAT,
  MAX_TURNS,
  CHUNK_CHAR_LIMIT,
  RATE_LIMIT_REPLY,
  BOT_DISCLOSURE,
  ATTACHMENT_REPLY,
  rateLimited,
  loadHistory,
  saveHistory,
  needsDisclosure,
  recordDiag,
  bumpDiagCount,
  sendWAMessage,
  chunkByChars,
  validSignature,
} from "../_lib/wa.js";

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  const debugKey = url.searchParams.get("debug");
  if (debugKey && debugKey === (env.WHATSAPP_VERIFY_TOKEN || "")) {
    let lastPost = null, lastMsg = null, count = null;
    if (env.LWD_KV) {
      try {
        const lp = await env.LWD_KV.get("wa:diag:lastpost");
        const lm = await env.LWD_KV.get("wa:diag:lastmsg");
        lastPost = lp ? JSON.parse(lp) : null;
        lastMsg = lm ? JSON.parse(lm) : null;
        count = await env.LWD_KV.get("wa:diag:count");
      } catch (e) { /* ignore */ }
    }
    return Response.json({
      ok: true,
      diag: {
        kvBound: Boolean(env.LWD_KV),
        tokenSet: Boolean(env.WHATSAPP_TOKEN),
        phoneIdEnv: env.WHATSAPP_PHONE_ID ? "set" : "not-set",
        webhookPostsSeen: count,
        lastPost,
        lastMsg,
      },
    });
  }

  const mode = url.searchParams.get("hub.mode");
  const token = url.searchParams.get("hub.verify_token");
  const challenge = url.searchParams.get("hub.challenge");
  if (mode === "subscribe" && token && token === (env.WHATSAPP_VERIFY_TOKEN || "")) {
    return new Response(challenge || "", { status: 200 });
  }
  return new Response("Forbidden", { status: 403 });
}

// ---------- POST: message aaya -> jawab do (background me) --------- //
export async function onRequestPost(context) {
  const { request, env, waitUntil } = context;

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
