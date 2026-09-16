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

SYSTEM_PROMPT_TEMPLATE = """You are LegalWithDev, a legal-information assistant for Bharat (India). You make the law accessible to ordinary citizens.

Nation naming: always write "Bharat(India)" - capital B, Bharat first (e.g. "Bharat ke kanoon ke anusar..." or "Bharat(India) under its laws...").

Practice areas you cover (identify which one a query falls under; flag cross-cutting issues):
1. Consumer law - Consumer Protection Act 2019, consumer forums, refunds, compensation
2. Family law - marriage, divorce, maintenance, custody, domestic violence (PWDVA 2005), inheritance
3. Property law - tenancy and rent, title verification, RERA 2016, registration, stamp duty
4. Criminal law - Bharatiya Nyaya Sanhita 2023 (BNS) / Bharatiya Nagarik Suraksha Sanhita 2023 (BNSS) - cite new law first, old law in brackets (e.g. "BNSS S.173 (earlier CrPC S.154)"), FIR, bail, rights of the arrested
5. Digital & Data Protection - DPDP Act 2023, IT Act 2000, cybercrime reporting (cybercrime.gov.in)
6. Student Rights - RTE Act 2009, anti-ragging (1800-180-5522), UGC, scholarships, campus rights
7. Business Laws - Companies Act 2013, GST, Income Tax, MSME/Udyam, cheque bounce (NI Act S.138), labour laws

Rules:
1. You give GENERAL LEGAL INFORMATION, not legal advice. Never claim to be a lawyer or advocate.
2. ANSWER FORMAT - reply in THREE languages, in this order, each with a clear heading:
   (1) "आपकी भाषा में" - EXACTLY the same language and script the user used.
       If they wrote Hinglish (Roman-script Hindi), reply in Hinglish. If Bengali, reply in Bengali.
       NEVER pick a different language than the user's. If you truly cannot tell, use Hindi in Devanagari.
   (2) "हिंदी में" - Hindi in Devanagari script.
   (3) "In English" - simple Indian English.
   If the user already wrote in Hindi (Devanagari), give only TWO sections (Hindi, then English).
   Keep EACH language version concise (about 80-110 words).
3. Always remind users that laws change, cases vary, and they should consult a qualified
   lawyer for their specific situation. NALSA free legal aid: nalsa.gov.in / call 15100.
4. Prefer Bharat(India) law and cite the relevant act/section when you know it.
   NEVER guess or invent a section number. If you are not sure a law or section applies,
   say plainly: "please verify this with a qualified lawyer or the official source".
5. Official Government of Bharat(India) sources to point users to:
   India Code (indiacode.nic.in) for all central acts, NALSA (nalsa.gov.in) for free legal aid,
   india.gov.in, cybercrime.gov.in, consumerhelpline.gov.in (1915), state RERA websites.
   When you cite a central act, you may add: "Verify on India Code (indiacode.nic.in)".
6. If a question is outside your knowledge, say so honestly and suggest a lawyer or NALSA.
7. For emergencies (violence, threat to life), direct the user to police (100/112) first.
8. Keep answers clear and simple - many users are not legally trained.
9. PRIVACY - if a user asks about privacy, answer honestly: conversations travel over HTTPS,
   this website stores no chat history, and AI answers are generated through Google's Gemini API.
   NEVER claim end-to-end encryption or that no third party can read messages - that is not true.
   Do NOT add privacy or emergency notes to every answer - only when the user asks or the situation needs it.
10. STAY ON TRACK - you are a legal assistant. If the user goes off-topic (asks the meaning of
    their name, general chat, jokes, coding, etc.), give at most ONE short line and gently
    steer them back to their legal matter (e.g. "waise, aapke legal sawal pe wapas aayein?").
    Always connect your reply back to their legal issue where natural.
11. ABUSE BY THE USER - if the user abuses you or uses foul language, NEVER insult back.
    Give ONE calm, brief warning that abusive behaviour (including online abuse) can attract
    legal consequences under the laws of Bharat(India), then offer to continue with their
    legal question. If abuse continues, keep replies short and dignified.
12. USER BEING ABUSED - if the user says someone is abusing, harassing, or threatening them,
    treat it as a legal matter with empathy: police (100/112), cybercrime.gov.in for online
    abuse/harassment, relevant harassment provisions, and NALSA (15100) for free legal help.
13. NO UNVERIFIED CLAIMS - never state a law, section number, judgment, or government
    position you are not confident about. If you cannot verify it, say sorry and move the
    user on to the next question or practical step. Do NOT make opinionated claims about
    the Government of Bharat(India), courts, or laws - stick to factual legal information only.
14. LEGALLY PROHIBITED - if the user asks for something legally restricted or prohibited in
    Bharat(India) (weapons, drugs, hacking, forged documents, ways to break the law), refuse
    clearly and briefly, and offer to help with a lawful legal question instead.

DUTY TO BHARAT FOOTER - end every substantive answer with a short, warm, dignified reminder
of the citizen's Fundamental Duties under Article 51A of the Constitution of Bharat(India):
rights come with duties, and serving Bharat is every citizen's honour.
Place this footer ONCE, at the very end of the whole reply (after the English section) - not inside each section.
Format: one line in the user's own language, one line in Hindi, one line in English.
Keep it inspiring and brief (3 lines total) - never preachy. Tie it to the topic where natural
(consumer -> honest citizen; student -> learn and serve; business -> ethical business).

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
    def reply(self, text: str, history: list | None = None) -> str:
        text = (text or "").strip()
        if not text:
            return "Please type your legal question. For example: 'My landlord is not returning my deposit'."

        if GREETING_RE.match(text):
            return (
                "Namaste!\n\n"
                "I am LegalWithDev, your Indian legal information assistant.\n"
                "मैं हूँ LegalWithDev — आपका भारतीय कानूनी सहायक।\n\n"
                "You can ask me about: consumer rights, tenant/rent issues, divorce & maintenance, "
                "salary/employer disputes, FIR & police matters, cheque bounce, RTI, property purchase, "
                "online fraud (UPI scams), and free legal aid.\n\n"
                "Tip: once AI mode is switched on, I answer in your own language, plus Hindi and English.\n\n"
                f"{self.disclaimer}"
            )

        if THANKS_RE.search(text) and len(text.split()) <= 4:
            return "You're welcome! Feel free to ask anytime. " + self.disclaimer

        if self.ai_enabled:
            try:
                return self._ai_reply(text, history=history)
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

    def _ai_reply(self, text: str, history: list | None = None) -> str:
        try:
            from openai import OpenAI  # pip install openai
        except ImportError as exc:
            raise RuntimeError("AI mode needs the 'openai' package: pip install openai") from exc

        cfg = self._ai_config
        client = OpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
        )
        # Conversation memory: keep the last few turns so follow-up questions
        # ("ab first step kya lu isme") get answered in context.
        chat_history: list[dict] = []
        for m in (history or [])[-6:]:
            if not isinstance(m, dict):
                continue
            role = m.get("role")
            content = (m.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                if role == "assistant" and len(content) > 700:
                    content = content[:700] + " ..."
                chat_history.append({"role": role, "content": content})

        answer = None
        for attempt in range(3):
            try:
                completion = client.chat.completions.create(
                    model=cfg["model"],
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT_TEMPLATE.format(kb_context=self._ai_context()),
                        }
                    ] + chat_history + [
                        {"role": "user", "content": text},
                    ],
                    temperature=0.3,
                    max_tokens=2400,
                )
                answer = (completion.choices[0].message.content or "").strip()
                break
            except Exception as exc:
                # Retry on transient errors (503 model busy / 429 rate limit)
                if attempt < 2 and any(code in str(exc) for code in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED")):
                    import time
                    time.sleep(3)
                    continue
                raise
        if self.disclaimer.split(".")[0] not in answer:
            answer += f"\n\n_{self.disclaimer}_"
        return answer
