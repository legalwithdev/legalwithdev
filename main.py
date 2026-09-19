"""
LegalWithDev - Legal AI Chatbot (web server).

Run:  uvicorn main:app --reload
Open: http://localhost:8000
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from agent import LegalAgent
from blogengine import router as blog_router

app = FastAPI(title="LegalWithDev - Legal AI Chatbot", version="0.2.0")
app.include_router(blog_router)
agent = LegalAgent()

# ------------------- rate limiting (per user/IP/chat) ------------------- #
_RATE_BUCKETS: dict[str, list[float]] = {}
RATE_LIMIT_WEB = 15    # messages per hour, per visitor (website)
RATE_LIMIT_CHAT = 20  # messages per hour, per user (Telegram / WhatsApp)

def _rate_limited(key: str, limit: int) -> bool:
    """True if this key has already hit `limit` messages in the last hour."""
    now = time.time()
    hits = [t for t in _RATE_BUCKETS.get(key, []) if now - t < 3600]
    _RATE_BUCKETS[key] = hits
    if len(hits) >= limit:
        return True
    hits.append(now)
    return False

RATE_LIMIT_REPLY = (
    "Aap bahut zyada messages bhej rahe hain. Thoda ruk kar phir try karein (1 ghante me limited sawal allowed hain).\n"
    "आप बहुत ज़्यादा संदेश भेज रहे हैं। थोड़ा रुककर फिर प्रयास करें।\n"
    "You are sending too many messages. Please wait a while and try again.\n\n"
    "Yeh free service hai - sab users ke liye available rakhne ke liye limit hai. NALSA: nalsa.gov.in / 15100."
)

HERE = Path(__file__).parent

@app.get("/translations.js")
def translations_js() -> FileResponse:
    return FileResponse(HERE / "translations.js", media_type="application/javascript", headers={"Cache-Control": "no-store"})

@app.get("/logo.png")
def logo_png() -> FileResponse:
    return FileResponse(HERE / "logo.png", media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})

@app.get("/favicon.png")
def favicon_png() -> FileResponse:
    return FileResponse(HERE / "favicon.png", media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

# ------------------- PWA (installable app) ------------------- #
@app.get("/manifest.json")
def manifest_json() -> FileResponse:
    return FileResponse(HERE / "manifest.json", media_type="application/manifest+json", headers={"Cache-Control": "no-store"})

@app.get("/sw.js")
def service_worker() -> FileResponse:
    return FileResponse(HERE / "sw.js", media_type="text/javascript", headers={"Cache-Control": "no-store"})

@app.get("/icon-192.png")
def icon_192() -> FileResponse:
    return FileResponse(HERE / "icon-192.png", media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

@app.get("/apple-touch-icon.png")
def apple_touch_icon() -> FileResponse:
    return FileResponse(HERE / "apple-touch-icon.png", media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

class ChatIn(BaseModel):
    message: str
    history: list[dict] = []  # optional conversation memory from the web UI
    language: str = ""  # optional language chosen in the website language selector (e.g. "Tamil")


# ------------------------- web chat ------------------------- #
@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    # no-store: browser ko har baar fresh page lene do, warna purana JS cache ho jata hai
    return HTMLResponse(
        (HERE / "index.html").read_text(encoding="utf-8"),
        headers={"Cache-Control": "no-store, must-revalidate"},
    )

@app.post("/api/chat")
async def chat(payload: ChatIn, request: Request) -> dict:
    visitor_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    if _rate_limited(f"web:{visitor_ip}", RATE_LIMIT_WEB):
        return {"reply": RATE_LIMIT_REPLY}
    reply = agent.ask(payload.message, history=payload.history, language=payload.language)
    return {"reply": reply}

# ------------------------- telegram ------------------------- #
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def tg_send(chat_id: int | str, text: str) -> dict:
    data = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        TG_API + "/sendMessage", data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception:
        return {}

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request) -> JSONResponse:
    global last_update_id
    try:
        update = await request.json()
    except Exception:
        return JSONResponse({"ok": True})
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()
    update_id = update.get("update_id", 0)
    if update_id <= last_update_id:
        return JSONResponse({"ok": True})
    last_update_id = update_id
    if not chat or not text:
        return JSONResponse({"ok": True})
    if _rate_limited(f"tg:{chat}", RATE_LIMIT_CHAT):
        tg_send(chat, RATE_LIMIT_REPLY)
        return JSONResponse({"ok": True})
    reply = agent.ask(text, history=[], language="")
    reply = reply.replace("*", "")
    tg_send(chat, reply)
    return JSONResponse({"ok": True})

last_update_id = 0

# ------------------------- whatsapp ------------------------- #
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID", "")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
WA_API = "https://graph.facebook.com/v21.0"

def wa_send(to: str, text: str) -> dict:
    url = f"{WA_API}/{WHATSAPP_PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {WHATSAPP_TOKEN}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception:
        return {}

@app.get("/webhook/whatsapp")
async def whatsapp_verify(request: Request) -> PlainTextResponse:
    """Meta GET webhook verification handshake."""
    mode = request.query_params.get("hub.mode", "")
    token = request.query_params.get("hub.verify_token", "")
    challenge = request.query_params.get("hub.challenge", "")
    if mode == "subscribe" and token and token == WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    return PlainTextResponse("Forbidden", status_code=403)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request) -> JSONResponse:
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"ok": True})
    entry_list = data.get("entry", [])
    for entry in entry_list:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                sender = msg.get("from", "")
                text = (msg.get("text", {}) or {}).get("body", "")
                if not sender or not text:
                    continue
                if _rate_limited(f"wa:{sender}", RATE_LIMIT_CHAT):
                    wa_send(sender, RATE_LIMIT_REPLY)
                    continue
                reply = agent.ask(text, history=[], language="")
                wa_send(sender, reply)
    return JSONResponse({"ok": True})
