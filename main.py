"""
LegalWithDev - Legal AI Chatbot (web server).

Run:  uvicorn main:app --reload
Open: http://localhost:8000
"""
from __future__ import annotations

import os
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from agent import LegalAgent

app = FastAPI(title="LegalWithDev - Legal AI Chatbot", version="0.1.0")
agent = LegalAgent()

HERE = Path(__file__).parent


class ChatIn(BaseModel):
    message: str
    history: list[dict] = []  # optional conversation memory from the web UI


# ------------------------- web chat ------------------------- #
@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    # no-store: browser ko har baar fresh page lene do, warna purana JS cache ho jata hai
    return HTMLResponse(
        (HERE / "index.html").read_text(encoding="utf-8"),
        headers={"Cache-Control": "no-store, must-revalidate"},
    )


@app.post("/api/chat")
def chat(payload: ChatIn) -> dict:
    return {"reply": agent.reply(payload.message, history=payload.history)}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "ai_mode": agent.ai_enabled,
        "topics": len(agent.topics),
    }


# ------------------- Telegram webhook ---------------------- #
# One service, no extra worker: Telegram sends updates here.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

TELEGRAM_ABOUT = (
    "LegalWithDev - Indian legal information assistant for Bharat.\n\n"
    "Poochho kuch bhi: consumer rights, tenant/rent issues, divorce & maintenance, "
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
    if len(_TELEGRAM_HISTORY) > _TELEGRAM_MAX_CHATS:  # drop oldest chats
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
        history = _TELEGRAM_HISTORY.get(chat_id, [])[-_TELEGRAM_MAX_TURNS:]
        reply = agent.reply(text, history=history)
        _remember(chat_id, text, reply)
        for i in range(0, len(reply), 4096):  # Telegram 4096-char limit
            send_telegram_message(chat_id, reply[i : i + 4096])
    return {"ok": True}


# ------------------- WhatsApp webhook ----------------------- #
def verify_whatsapp_webhook(query_params: dict):
    """Meta's webhook verification handshake (GET with hub.challenge)."""
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge", "")
    expected = os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me")
    if mode == "subscribe" and token == expected:
        return int(challenge)
    return {"status": "rejected"}


def handle_whatsapp_message(payload: dict, agent) -> list[str]:
    """Extract inbound WhatsApp text messages, answer with the agent.
    To actually SEND the reply, activate send_whatsapp_text below once
    you have WHATSAPP_TOKEN and WHATSAPP_PHONE_ID configured."""
    replies: list[str] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                if message.get("type") == "text":
                    text = message.get("text", {}).get("body", "")
                    reply = agent.reply(text)
                    replies.append(reply)
                    # send_whatsapp_text(message["from"], reply)
    return replies


def send_whatsapp_text(to_phone: str, body: str) -> dict:
    """Send a WhatsApp text message via the Meta Cloud API."""
    import requests  # pip install requests

    token = os.environ["WHATSAPP_TOKEN"]
    phone_id = os.environ["WHATSAPP_PHONE_ID"]
    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"body": body[:4096]},
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


@app.get("/webhook/whatsapp")
def whatsapp_verify(request: Request):
    return verify_whatsapp_webhook(request.query_params)


@app.post("/webhook/whatsapp")
async def whatsapp_receive(request: Request):
    payload = await request.json()
    replies = handle_whatsapp_message(payload, agent)
    return JSONResponse({"handled": len(replies)})
