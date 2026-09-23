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

  // sab kaam background me - Meta ko turant 200 (warna wo retry karta hai aur replies duplicate ho jaate hain)
  const task = (async () => {
    const token = env.WHATSAPP_TOKEN || "";
    const brain = createBrain(env);
    await bumpDiagCount(env);

    const entries = payload.entry || [];
    for (const entry of entries) {
      const changes = entry.changes || [];
      for (const change of changes) {
        const value = (change && change.value) || {};
        if (value.statuses && value.statuses.length) continue;

        const phoneId =
          (value.metadata && value.metadata.phone_number_id) ||
          env.WHATSAPP_PHONE_ID ||
          "";
        const messages = value.messages || [];
        if (messages.length) {
          await recordDiag(env, "wa:diag:lastpost", {
            at: new Date().toISOString(),
            msgs: messages.length,
            from: String((messages[0] && messages[0].from) || ""),          });
        }
        for (const msg of messages) {
          const from = msg.from;
        if (!from) continue;

          // dedup: ek hi message ID dobara aaye to skip (Meta retry protection)
          if (env.LWD_KV && msg.id) {
            try {
              const seen = await env.LWD_KV.get("wa:seen:" + msg.id);
              if (seen) continue;
              await env.LWD_KV.put("wa:seen:" + msg.id, "1", { expirationTtl: 900 });
            } catch (e) { /* ignore */ }
          }

          const text = String((msg.text && msg.text.body) || "").trim();
          if (!text) {
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

          let lastSend = null;
          for (const chunk of chunkByChars(reply, CHUNK_CHAR_LIMIT)) {
            lastSend = await sendWAMessage(token, phoneId, from, chunk);
          }
          await recordDiag(env, "wa:diag:lastmsg", {
            at: new Date().toISOString(),
            from,
            type: msg.type || "text",
            textLen: text.length,
            replyLen: reply.length,
            send: lastSend,
          });
        }
      }
    }
  })();

  if (waitUntil) {
    waitUntil(task);
  } else {
    await task;
  }
  return Response.json({ ok: true });
}
