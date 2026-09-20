/* LegalWithDev service worker - v4
   Strategy (safe for a chat app on a free tier):
   - HTML pages + translations.js + blog: NETWORK-FIRST (user always gets fresh
     content when online), cache fallback only when offline.
   - Static assets (logo, icons): CACHE-FIRST.
   - NEVER touch: /api/* (chat POST), /webhook/* (Telegram/WhatsApp),
     third-party requests, and anything that is not a GET.
   This means: chat always needs the server; offline users get the last cached
   page shell instead of a browser error page.
   v4: /app bhi network-first - ek interface har jagah (purana cached app UI hata gaya).
*/
const CACHE = "lwd-static-v4";
const PRECACHE = [
  "/logo.png",
  "/favicon.png",
  "/icon-192.png",
  "/apple-touch-icon.png",
  "/manifest.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/webhook/")) return;

  const dynamic = url.pathname === "/" || url.pathname === "/app" || url.pathname === "/translations.js" || url.pathname.startsWith("/blog");
  if (dynamic) {
    // network-first: freshness matters more than speed here
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((m) => m || caches.match("/")))
    );
    return;
  }

  // static assets: cache-first
  event.respondWith(
    caches.match(req).then(
      (m) =>
        m || fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy));
          return res;
        })
    )
  );
});