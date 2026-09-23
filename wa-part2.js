
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
