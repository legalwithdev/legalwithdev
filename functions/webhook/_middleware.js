// functions/webhook/_middleware.js - /webhook/* ka flight recorder (POST counter)
// Sirf count + last path/time likhta hai KV me. next() se route handler normal chalta hai.
export async function onRequest(context) {
  const { request, env, next } = context;
  if (request.method === "POST" && env.LWD_KV) {
    try {
      const url = new URL(request.url);
      const c = Number((await env.LWD_KV.get("http:posts:count")) || "0") + 1;
      await env.LWD_KV.put("http:posts:count", String(c), { expirationTtl: 3 * 24 * 3600 });
      await env.LWD_KV.put(
        "http:posts:last",
        JSON.stringify({ at: new Date().toISOString(), path: url.pathname }),
        { expirationTtl: 3 * 24 * 3600 }
      );
    } catch (e) { /* ignore */ }
  }
  return next();
}
