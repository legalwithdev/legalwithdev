// functions/webhook/wadebug.js - GET /webhook/wadebug?debug=<VERIFY_TOKEN>[&send=1&to=<wa_id>][&check=1][&fix=1]
// Bot ka black-box: token set hai?, webhook POST aaye?, aur (send=1 par) Graph API se
// seedha test message bhej kar uska EXACT status/error dikhaata hai. User content store nahi hota.
export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const key = url.searchParams.get("debug") || "";
  if (key !== (env.WHATSAPP_VERIFY_TOKEN || "")) {
    return new Response("Forbidden", { status: 403 });
  }

  const diag = {
    at: new Date().toISOString(),
    tokenSet: Boolean(env.WHATSAPP_TOKEN),
    kvBound: Boolean(env.LWD_KV),
    phoneIdEnv: env.WHATSAPP_PHONE_ID || "",
  };
  if (env.LWD_KV) {
    try {
      diag.postsCount = await env.LWD_KV.get("http:posts:count");
      const lp = await env.LWD_KV.get("http:posts:last");
      diag.lastPost = lp ? JSON.parse(lp) : null;
    } catch (e) { /* ignore */ }
  }

  if (url.searchParams.get("send") === "1") {
    const to = url.searchParams.get("to") || "";
    const token = env.WHATSAPP_TOKEN || "";
    const phoneId = env.WHATSAPP_PHONE_ID || "";
    if (!token || !phoneId || !to) {
      diag.testSend = { error: "need WHATSAPP_TOKEN + WHATSAPP_PHONE_ID + to" };
    } else {
      try {
        const res = await fetch(
          "https://graph.facebook.com/v21.0/" + phoneId + "/messages",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + token,
            },
            body: JSON.stringify({
              messaging_product: "whatsapp",
              recipient_type: "individual",
              to: to,
              type: "text",
              text: { body: "LegalWithDev test message (diagnostic) - agar ye aaya to bot ka send kaam kar raha hai." },
            }),
          }
        );
        diag.testSend = { status: res.status, body: (await res.text()).slice(0, 300) };
      } catch (e) {
        diag.testSend = { status: -1, error: String((e && e.message) || e) };
      }
    }
  }

  const wabaId = "1443459081005286";
  const auth = "Bearer " + (env.WHATSAPP_TOKEN || "");
  if (url.searchParams.get("check") === "1") {
    try {
      const res = await fetch("https://graph.facebook.com/v21.0/" + wabaId + "/subscribed_apps", {
        headers: { Authorization: auth },
      });
      diag.subscribedApps = { status: res.status, body: (await res.text()).slice(0, 400) };
    } catch (e) {
      diag.subscribedApps = { error: String((e && e.message) || e) };
    }
  }
  if (url.searchParams.get("fix") === "1") {
    try {
      const res = await fetch(
        "https://graph.facebook.com/v21.0/" + wabaId + "/subscribed_apps?subscribed_fields=messages",
        { method: "POST", headers: { Authorization: auth } }
      );
      diag.fixSubscribe = { status: res.status, body: (await res.text()).slice(0, 400) };
    } catch (e) {
      diag.fixSubscribe = { error: String((e && e.message) || e) };
    }
  }
  return Response.json({ ok: true, diag });
}
