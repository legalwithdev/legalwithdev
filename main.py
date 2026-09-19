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
    "à¤†à¤ª à¤¬à¤¸à¥€à¤¤ à¤œà¤¼à¥à¸ƒ‚’£‚’âà´›‚’£‚–”-7‚’Ë‚’ÿ‚–‚’Èƒ‚’×‚–‚’pƒ‚’Ã‚’ç‚–ƒ‚’ç‚–#‚’‚–ƒ‚’—‚–/‚’‡‚’ó‚’øƒ‚’Ã‚–‚’W‚’W‚’Àƒ‚’¯‚’ÿ‚’Àƒ‚’«‚–7‚’Ã‚’¿‚’û‚’àƒ‚’W‚’Ã‚–‚’‚–‘q¸ˆ(€€€€‰e½Ô…É”Í•¹‘¥¹œÑ½¼µ…¹äµ•ÍÍ…•Ì¸A±•…Í”İ…¥Ğ„İ¡¥±”…¹ÑÉä……¥¸¹q¹q¸ˆ(€€€€‰e• ™É•”Í•ÉÙ¥”¡…¤€´Í…ˆÕÍ•ÉÌ­”±¥å”…Ù…¥±…‰±”É…­¡¹”­”±¥å”±¥µ¥Ğ¡…¤¸91Mè¹…±Í„¹½Ø¹¥¸€¼€ÄÔÄÀÀ¸ˆ(¤()!I€ôA…Ñ ¡}}™¥±•}|¤¹Á…É•¹Ğ(()…ÁÀ¹•Ğ ˆ½ÑÉ…¹Í±…Ñ¥½¹Ì¹©Ìˆ¤)‘•˜ÑÉ…¹Í±…Ñ¥½¹Í}©Ì ¤€´ø¥±•I•ÍÁ½¹Í”è(€€€É•ÑÕÉ¸¥±•I•ÍÁ½¹Í”¡!I€¼€‰ÑÉ…¹Í±…Ñ¥½¹Ì¹©Ìˆ°µ•‘¥…}ÑåÁ”ô‰…ÁÁ±¥…Ñ¥½¸½©…Ù…ÍÉ¥ÁĞˆ°¡•…‘•ÉÌõì‰…¡”µ½¹ÑÉ½°ˆè€‰¹¼µÍÑ½É”‰ô¤(()…ÁÀ¹•Ğ ˆ½±½¼¹Á¹œˆ¤)‘•˜±½½}Á¹œ ¤€´ø¥±•I•ÍÁ½¹Í”è(€€€É•ÑÕÉ¸¥±•I•ÍÁ½¹Í”¡!I€¼€‰±½¼¹Á¹œˆ°µ•‘¥…}ÑåÁ”ô‰¥µ…”½Á¹œˆ°¡•…‘•ÉÌõì‰…¡”µ½¹ÑÉ½°ˆè€‰ÁÕ‰±¥Œ°µ…àµ…”ôÌØÀÀ‰ô¤(()…ÁÀ¹•Ğ ˆ½™…Ù¥½¸¹Á¹œˆ¤)‘•˜™…Ù¥½¹}Á¹œ ¤€´ø¥±•I•ÍÁ½¹Í”è(€€€É•ÑÕÉ¸¥±•I•ÍÁ½¹Í”¡!I€¼€‰™…Ù¥½¸¹Á¹œˆ°µ•‘¥…}ÑåÁ”ô‰¥µ…”½Á¹œˆ°¡•…‘•ÉÌõì‰…¡”µ½¹ÑÉ½°ˆè€‰ÁÕ‰±¥Œ°µ…àµ…”ôàØĞÀÀ‰ô¤(()±…ÍÌ¡…Ñ%¸¡	…Í•5½‘•°¤è(€€€µ•ÍÍ…”èÍÑÈ(€€€¡¥ÍÑ½Éäè±¥ÍÑm‘¥Ñt€ômt€€Œ½ÁÑ¥½¹…°½¹Ù•ÉÍ…Ñ¥½¸µ•µ½Éä™É½´Ñ¡”İ•ˆU$(€€€±…¹Õ…”èÍÑÈ€ô€ˆˆ€€Œ½ÁÑ¥½¹…°±…¹Õ…”¡½Í•¸¥¸Ñ¡”İ•‰Í¥Ñ”±…¹Õ…”Í•±•Ñ½È€¡”¹œ¸€‰Q…µ¥°ˆ¤(((Œ€´´´´´´´´´´´´´´´´´´´´´´´´´İ•ˆ¡…Ğ€´´´´´´´´´´´´´´´´´´´´´´´´´€Œ)…ÁÀ¹•Ğ ˆ¼ˆ°É•ÍÁ½¹Í•}±…ÍÌõ!Q51I•ÍÁ½¹Í”¤)‘•˜¥¹‘•à ¤€´ø!Q51I•ÍÁ½¹Í”è(€€€€Œ¹¼µÍÑ½É”è‰É½İÍ•È­¼¡…È‰……È™É•Í Á…”±•¹”‘¼°İ…É¹„ÁÕÉ…¹„)L…¡”¡¼©…Ñ„¡…¤(€€€É•ÑÕÉ¸!Q51I•ÍÁ½¹Í” (€€€€€€€€¡!I€¼€‰¥¹‘•à¹¡Ñµ°ˆ¤¹É•…‘}Ñ•áĞ¡•¹½‘¥¹œô‰ÕÑ˜´àˆ¤°(€€€€€€€¡•…‘•ÉÌõì‰…¡”µ½¹ÑÉ½°ˆè€‰¹¼µÍÑ½É”°µÕÍĞµÉ•Ù…±¥‘…Ñ”‰ô°(€€€€¤(()…ÁÀ¹Á½ÍĞ ˆ½…Á¤½¡…Ğˆ¤)…Íå¹Œ‘•˜¡…Ğ¡Á…å±½…è¡…Ñ%¸°É•ÅÕ•ÍĞèI•ÅÕ•ÍĞ¤€´ø‘¥Ğè(€€€Ù¥Í¥Ñ½É}¥À€ôÉ•ÅÕ•ÍĞ¹¡•…‘•ÉÌ¹•Ğ ‰àµ™½Éİ…É‘•µ™½Èˆ°É•ÅÕ•ÍĞ¹±¥•¹Ğ¹¡½ÍĞ¥˜É•ÅÕ•ÍĞ¹±¥•¹Ğ•±Í”€‰Õ¹­¹½İ¸ˆ¤(€€€¥˜}É…Ñ•}±¥µ¥Ñ•¡˜‰İ•ˆéíÙ¥Í¥Ñ½É}¥Áôˆ°IQ}1%5%Q}]¤è(€€€€€€€É•ÑÕÉ¸ì‰É•Á±äˆèIQ}1%5%Q}IA1eô(€€€É•ÑÕÉ¸ì‰É•Á±äˆè…•¹Ğ¹É•Á±ä¡Á…å±½…¹µ•ÍÍ…”°¡¥ÍÑ½ÉäõÁ…å±½…¹¡¥ÍÑ½Éä°±…¹Õ…”õÁ…å±½…¹±…¹Õ…”¥ô(()…ÁÀ¹•Ğ ˆ½¡•…±Ñ ˆ¤)‘•˜¡•…±Ñ  ¤€´ø‘¥Ğè(€€€É•ÑÕÉ¸ì(€€€€€€€€‰ÍÑ…ÑÕÌˆè€‰½¬ˆ°(€€€€€€€€‰…¥}µ½‘”ˆè…•¹Ğ¹…¥}•¹…‰±•°(€€€€€€€€‰Ñ½Á¥Ìˆè±•¸¡…•¹Ğ¹Ñ½Á¥Ì¤°(€€€ô(((Œ€´´´´´´´´´´´´´´´´´´´´´´´´´ÁÉ¥Ù…äÁ½±¥ä€´´´´´´´´´´´´´´´´´´------- #
PRIVACY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Privacy Policy â€” LegalWithDev</title>
<style>
  body { font-family: system-ui, sans-serif; background: #0b1020; color: #e8edf7; margin: 0; padding: 24px 18px; line-height: 1.7; }
  .card { max-width: 680px; margin: 0 auto; background: #151d33; border: 1px solid #232d4a; border-radius: 16px; padding: 28px 26px; }
  h1 { font-size: 22px; margin: 0 0 4px; } h2 { font-size: 16px; color: #8aa2ff; margin: 24px 0 6px; }
  p, li { font-size: 14.5px; color: #c7d0e4; } .muted { color: #8b95ad; font-size: 12.5px; }
  a { color: #8aa2ff; }
</style>
</head>
<body><div class="card">
<h1>âš›e Ar WithDewâ˜• Privacy Policy</h1>
<p class="muted">Last updated: 17 September 2026</p>

<h2>1. Kya store hota hai</h2>
<p>Hamari website par aapki chat history <strong>server par store nahi hotai</strong>. Baat-cheet sirf aapke browser ki memory (RAM) me rehti hai aur page band karne par chali jaati hai.</p>
<p>Telegram / WhatsApp par, aapke recent messages sirf <strong>conversation context yaad rakhne ke liie</strong> server ki temporary memory (RAM) me rehte hain. Yeh data disk par save nahi hota aur server restart hone par clear ho jata hai.</p>

<h2>2. Aapka data kahan jaata hai</h2>
<p>Jab aap sawal poochte hain, woh message <strong>HTTPS (encrypted) connection</strong> par hamare server tak aata hai, aur AI jawab banane ke liye <strong>Google Gemini API</strong> ko bheja jaata hai.</p>
<p><strong>Google ke Unpaid (Free) Tier ke terms ke mutabik:</strong> free tier par Google aapke submitted content aur AI responses ko apne products aur machine learning ko improve karne ke liye use kar sakta hai, aur quality ke liye <strong>human reviewers bhi is data ko padh sakte hain</strong> (Google data ko aapke account/API key se alag karke dikhaata hai). Isliye Google khud kehta hai: <strong>"Do not submit sensitive, confidential, or personal information to the Unpaid Services"</strong>.</p>
<p><strong>ğŸ”’ Isliye humari request:</strong> chat me apna sensitive personal information â€” naam, case numbers, documents, address, Aadhaar â€” <strong>share na karein</strong>. Apna sawal general bhasha me poochhiye (jaise: "landlord deposit wapas nahi kar raha, kya karu?").</p>
<p>Hum aapka data kisi ko <strong>bechte nahi</strong>, aur apni taraf se kisi <strong>AI training me use nahi karte</strong>.</p>

<h2>3. Rate limiting</h2>
<p>Service sabke liye free rakhne ke liye, har user/IP par ek ghante me limited messages ki limit hai (abuse/spam se bachne ke liye).</p>

<h2>4. Kya NAHI karte</h2>
<ul>
<li>Naam, phone, address ya case details maangna ya save karna</li>
<li>Data bechna ya advertising ke liye use karna</li>
<li>Chat history wapas padhna (store hi nahi hoti)</li>
</ul>

<h2>5. Contact & Disclaimer</h2>
<p>LegalWithDev ek <strong>AI legal-information assistant</strong> hai â€” advocate nahi. Yeh general legal information deta hai, legal advice nahi. Apne case ke liye qualified Advocate/Lawyer se milein. Free legal aid: <a href="https://nalsa.gov.in">nalsa.gov.in</a> Â· 15100.</p>
<p>Questions? Email: <strong>legalwithdev@gmail.com</strong></p>
</div></body>
</html>"""


@app.get("/privacy", response_class=HTMLResponse)
def privacy() -> HTMLResponse:
    return HTMLResponse(PRIVACY_HTML, headers={"Cache-Control": "no-store, must-revalidate"})


# ---------------------- Telegram webhook ----------------------- #
# One service, no extra worker: Telegram sends updates here.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

TELEGRAM_ABOUT = (
    "LegalWithDev - Indian legal information assistant for Bharat.\n\n"
    "Poochho kuch bhu: consumer rights, tenant/rent issues, divorce & maintenance, "
    "salary disputes, FIR & police matters, cheque bounce, RTI, property, ragging, "
    "online fraud (UPI scams), aur free legal aid.\n\n"
    "Answers in your native language + Hindi + English.\n\n" + agent.disclaimer
)

# ---- per-chat conversation memory (Telegram) ---- #
_TELEGRAM_HISTORY: dict[int, list] = {}
_TELEGRAM_MAX_TURNS = 6   # messages of context per chat
_TELEGRAM_MAX_CHATS = 200  # safety cap so memory never grows unbounded


def _remember(chat_id: int, user_text: str, bot_reply: str) -> None:
    hist = _TELEGRAM_HISTORY.setdefault(chat_id, [])
    hist.append({"role": "user", "content": user_text})
    hist.append({"role": "assistant", "content": bot_reply[:700]})
    del hist[:-_TELEGRAM_MAX_TURNS]
    if len(_TELEGRAM_HISTORY) > _TELEGRAM_MAX_CHATS: # drop oldest chats
        _TELEGRAM_HISTORY.pop(next(iter(_TELEGRAM_HISTORY)))


def send_telegram_message(chat_id: int, text: str) -> None:
    """Fire-and-forget reply to the user on Telegram (no extra libraries needed)."""
    if not TELEGRAM_BOT_TOKEN:
        return
    try:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data=data,
            timeout=15,
        )
    except Exception:
        pass  # never crash the bot because one reply failed


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    update = await request.json()
    message = update.get("message") or update.get("edited_message") or {}
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()
    if not chat_id:
        return {"ok": True}
    if text.startswith("/start") or text.startswith("/help"):
        send_telegram_message(chat_id, TELEGRAM_ABOUT)
    elif text:
        if _rate_limited(f"tg:{chat_id}", RATE_LIMIT_CHAT):
            send_telegram_message(chat_id, RATE_LIMIT_REPLY)
            return {"ok": True}
        history = _TELEGRAM_HISTORY.get(chat_id, [])[-_TELEGRAM_MAX_TURNS:]
        reply = agent.reply(text, history=history)
        _remember(chat_id, text, reply)
        for i in range(0, len(reply), 4096):  # Telegram 4096-char limit
            send_telegram_message(chat_id, reply[i : i + 4096])
    return {"ok": True}


# ------------------- WhatsApp webhook ----------------------- #
# ---- per-chat conversation memory (WhatsApp) ---- #
_WHATSAPP_HISTORY: dict[str, list] = {}
_WHATSAPP_MAX_TURNS = 6    # messages of context per chat
_WHATSAPP_MAX_CHATS = 200  # safety cap


def _wa_remember(sender: str, user_text: str, bot_reply: str) -> None:
    hist = _WHATSAPP_HISTORY.setdefault(sender, [])
    hist.append({"role": "user", "content": user_text})
    hist.append({"role": "assistant", "content": bot_reply[:700]})
    del hist[:-_WHATSAPP_MAX_TURNS]
    if len(_WHATSAPP_HISTORY) > _WHATSAPP_MAX_CHATS:
        _WHATSAPP_HISTORY.pop(next(iter(_WHATSAPP_HISTORY)))


def verify_whatsapp_webhook(query_params: dict):
    """Meta's webhook verification handshake (GET with hub.challenge)."""
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge", "")
    expected = os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me")
    if mode == "subscribe" and token == expected:
        # Echo the challenge back EXACTLY as Meta sent it, as plain text.
        # Never int() it - Meta may send non-numeric challenge strings.
        return PlainTextResponse(content=challenge)
    return PlainTextResponse(status_code=403)


def handle_whatsapp_message(payload: dict, agent) -> list[str]:
    """Extract inbound WhatsApp text messages, answer with the agent,
    and send the reply back via the Meta Cloud API (if configured)."""
    replies: list[str] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                if message.get("type") != "text":
                    continue
                text = (message.get("text", {}).get("body") or "").strip()
                sender = message.get("from") or ""
                if not text or not sender:
                    continue
                if _rate_limited(f"wa:{sender}", RATE_LIMIT_CHAT):
                    replies.append(RATE_LIMIT_REPLY)
                    send_whatsapp_text(sender, RATE_LIMIT_REPLY[:4000])
                    continue
                history = _WHATSAPP_HISTORY.get(sender, [])[-_WHATSAPP_MAX_TURNS:]
                reply = agent.reply(text, history=history)
                _wa_remember(sender, text, reply)
                replies.append(reply)
                send_whatsapp_text(sender, reply[:4000])
    return replies


def send_whatsapp_text(to_phone: str, body: str) -> dict | None:
    """Send a WhatsApp text message via the Meta Cloud API (no extra library needed).
    Silently skips if WHATSAPP_TOKEN / WHATSAPP_PHONE_ID are not set."""
    token = os.getenv("WHATSAPP_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_ID", "")
    if not token or not phone_id:
        return None
    try:
        data = urllib.parse.urlencode(
            {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "body": body,
            }
        ).encode()
        req = urllib.request.Request(
            f"https://graph.facebook.com/v21.0/{phone_id}/messages",
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode() or "{}")
    except Exception:
        return None  # never crash the webhook because one reply failed


@app.get("/webhook/whatsapp")
def whatsapp_verify(request: Request):
    return verify_whatsapp_webhook(request.query_params)


@app.post("/webhook/whatsapp")
async def whatsapp_receive(request: Request):
    payload = await request.json()
    replies = handle_whatsapp_message(payload, agent)
    return JSONResponse({"handled": len(replies)})
