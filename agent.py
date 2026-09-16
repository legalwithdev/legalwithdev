"""
Core Legal AI Agent.

Two modes, chosen automatically:
1. AI mode   - if AI_API_KEY is set in .env, uses any OpenAI-compatible
              chat-completion API (Sarvam AI, OpenAI, Groq, Ollama, etc.)
              for free-form conversation, grounded with the knowledge base.
2. Local mode - zero configuration: matches your question to a curated
              Indian-law knowledge base. Works with no API key at all.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Optional

KB_PATH = Path(__file__).parent / "indian_law_kb.json"

GREETING_RE = re.compile(
    r"^(hi|hii+|hey|hello|namaste|namaskar|good (morning|afternoon|evening)|yo|salaam)\b",
    re.IGNORECASE,
)
THANKS_RE = re.compile(r"\b(thanks|thank you|thx|dhanyawad|shukriya)\b", re.IGNORECASE)

SYSTEM_PROMPT_TEMPLATE = """You are LegalWithDev, a helpful legal-information assistant for India.
Rules:
1. You give GENERAL LEGAL INFORMATION, not legal advice. Never claim to be a lawyer.
2. Always remind users that laws change, cases vary, and they should consult a qualified
   lawyer for their specific situation. NALSA free legal aid: nalsa.gov.in / call 15100.
3. Prefer Indian law and cite the relevant act/section when you know it.
4. If a question is outside your knowledge, say so honestly and suggest a lawyer or NALSA.
5. For emergencies (violence, threat to life), direct the user to police (100/112) first.
6. Reply in the language the user writes in (English, Hindi, Hinglish, etc.).
7. Keep answers clear and simple - many users are not legally trained.

Reference knowledge base (use when relevant):
{kb_context}"""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).lower()
    return re.sub(r"[^\w\s]", " ", text)


def _tokens(text: str) -> set[str]:
    return set(_norm(text).split())


def _score(query: str, topic: dict) -> float:
    q = _tokens(query)
    if not q:
        return 0.0
    hits = 0
    for kw in topic.get("keywords", []):
        kw_t = _tokens(kw)
        if kw_t and kw_t.issubset(q):
            hits += len(kw_t)
    # also count title-word overlap lightly
    title_t = _tokens(topic["title"])
    hits += 0.5 * len(q & title_t)
    return hits


class LegalAgent:
    """The brain of the chatbot. Channel-agnostic: every channel (web,
    Telegram, WhatsApp) calls `agent.reply(text)` and gets an answer string."""

    def __init__(self) -> None:
        self.kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
        self.topics = self.kb["topics"]
        self.disclaimer = self.kb["disclaimer"]
        self.ai_enabled = bool(os.getenv("AI_API_KEY"))
        self._ai_config = {
            "base_url": os.getenv("AI_BASE_URL", "https://api.sarvam.ai/v1").rstrip("/"),
            "model": os.getenv("AI_MODEL", "sarvam-m"),
            "api_key": os.getenv("AI_API_KEY", ""),
        }

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def reply(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return "Please type your legal question. For example: 'My landlord is not returning my deposit'."

        if GREETING_RE.match(text):
            return (
                "Namaste! I am LegalWithDev, your Indian legal information assistant.\n\n"
                "You can ask me about: consumer rights, tenant/rent issues, divorce & maintenance, "
                "salary/employer disputes, FIR & police matters, cheque bounce, RTI, property purchase, "
                "online fraud (UPI scams), and free legal aid.\n\n"
                f"{self.disclaimer}"
            )

        if THANKS_RE.search(text) and len(text.split()) <= 4:
            return "You're welcome! Feel free to ask anytime. " + self.disclaimer

        if self.ai_enabled:
            try:
                return self._ai_reply(text)
            except Exception as exc:  # noqa: BLE001 - fall back gracefully
                local = self._local_reply(text)
                return local + f"\n\n(AI backend error: {exc})"

        return self._local_reply(text)

    # ------------------------------------------------------------------ #
    # Local (no-API-key) mode
    # ------------------------------------------------------------------ #
    def _local_reply(self, text: str) -> str:
        ranked = sorted(
            ((t, _score(text, t)) for t in self.topics),
            key=lambda x: x[1],
            reverse=True,
        )
        best, score = ranked[0]
        if score >= 1:
            others = ", ".join(t["title"] for t, s in ranked[1:4] if s >= 1)
            extra = (
                f"\n\nI also know a bit about: {others} - just ask!"
                if others
                else ""
            )
            return (
                f"**{best['title']}**\n\n{best['answer']}{extra}\n\n"
                f"_{self.disclaimer}_"
            )

        # No confident match - list capabilities instead of guessing.
        titles = "\n".join(f"• {t['title']}" for t in self.topics)
        return (
            "I'm not sure about that one yet - my built-in knowledge covers these areas:\n\n"
            f"{titles}\n\n"
            "To enable free-form answers on ANY legal question, connect an AI model "
            "(see the README, section 'Connecting an AI brain').\n\n"
            f"{self.disclaimer}"
        )

    # ------------------------------------------------------------------ #
    # AI mode (any OpenAI-compatible endpoint)
    # ------------------------------------------------------------------ #
    def _ai_context(self) -> str:
        parts = []
        for t in self.topics:
            parts.append(f"## {t['title']}\n{t['answer']}\nSources: {', '.join(t.get('sources', []))}")
        return "\n\n".join(parts)

    def _ai_reply(self, text: str) -> str:
        try:
            from openai import OpenAI  # pip install openai
        except ImportError as exc:
            raise RuntimeError("AI mode needs the 'openai' package: pip install openai") from exc

        cfg = self._ai_config
        client = OpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
        )
        completion = client.chat.completions.create(
            model=cfg["model"],
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_TEMPLATE.format(kb_context=self._ai_context()),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.3,
            max_tokens=700,
        )
        answer = (completion.choices[0].message.content or "").strip()
        if self.disclaimer.split(".")[0] not in answer:
            answer += f"\n\n_{self.disclaimer}_"
        return answer
