"""
LegalWithDev - Legal AI Chatbot (web server).

Run:  uvicorn main:app --reload
Open: http://localhost:8000
"""
from __future__ import annotations

import os
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


# ------------------------- web chat ------------------------- #
@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((HERE / "index.html").read_text(encoding="utf-8"))


@app.post("/api/chat")
def chat(payload: ChatIn) -> dict:
    return {"reply": agent.reply(payload.message)}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "ai_mode": agent.ai_enabled,
        "topics": len(agent.topics),
    }


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
