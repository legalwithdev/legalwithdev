#!/usr/bin/env bash
# LegalWithDev - Cloudflare Pages build (Option B)
# Static site banata hai (dist/): sab files repo se, blog/privacy live Render se snapshot.
# CI me chalta hai (Cloudflare Pages), locally bhi chal sakta hai:
#   RENDER_BASE=http://localhost:8073 bash build.sh
set -e
RENDER_BASE="${RENDER_BASE:-https://legalwithdev.onrender.com}"

mkdir -p dist/blog/free-legal-aid-guide dist/about dist/shop dist/privacy

# 1) index.html: chat API ko Render pe point karo (pages.dev pe /api/chat nahi hai)
sed "s|fetch('/api/chat'|fetch('${RENDER_BASE}/api/chat'|" index.html > dist/index.html

# 2) seedhe static files
cp about.html dist/about/index.html
cp shop.html dist/shop/index.html
cp translations.js sw.js manifest.json robots.txt sitemap.xml dist/
cp logo.png favicon.png icon-192.png apple-touch-icon.png dist/

# 3) /app purane links -> /
echo "/app / 307" > dist/_redirects

# 4) blog + privacy: Render wahi HTML serve karta hai - snapshot le lo
#    (Render so raha ho to pehli curl ~30s leti hai, build timeout se kahin kam hai)
curl -sf --max-time 120 "$RENDER_BASE/blog" -o dist/blog/index.html
curl -sf --max-time 120 "$RENDER_BASE/blog/free-legal-aid-guide" -o dist/blog/free-legal-aid-guide/index.html
curl -sf --max-time 120 "$RENDER_BASE/privacy" -o dist/privacy/index.html

echo "--- dist/ ready ---"
ls -la dist/ dist/blog/
