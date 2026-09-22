# LegalWithDev — Legal AI Chatbot for India ⚖️

A chatbot that answers **general questions about Indian law** (consumer rights,
tenant issues, family law, salary disputes, FIR/police, cheque bounce, RTI,
property, online fraud, free legal aid). All legal answers were fact-checked
in September 2026.

This is the **mobile-friendly flat version** — no folders, so you can upload
everything to GitHub straight from a phone.

> ⚠️ The bot gives *general legal information*, never legal advice.
> Free legal aid in India: nalsa.gov.in or call 15100.

## Files

| File | What it is |
|---|---|
| `main.py` | The web server + WhatsApp webhook |
| `agent.py` | The "brain" — matches questions to legal answers |
| `indian_law_kb.json` | Knowledge base (edit to add topics!) |
| `index.html` | The chat page users see |
| `telegram_bot.py` | Telegram bot (optional) |
| `requirements.txt` | Python packages needed |
| `render.yaml` | Render.com deploy settings |

## How to go LIVE from a phone (no computer needed)

**You need:** a phone, the extracted files, and about 30 minutes.

### Part 1 — Extract the files
1. Open your **Files app** and find `legalwithdev-mobile.zip`.
2. Tap it → **Extract** (on Android: Files by Google → long-press zip → Extract;
   on iPhone: Files app → tap the zip once — it unzips automatically).
3. Remember which folder the 7 files went to.

### Part 2 — GitHub (about 10 minutes)
4. Open **Chrome** → go to **github.com** → **Sign up** (free).
5. Turn ON **"Desktop site"** in Chrome's menu (⋮) — important!
6. Tap the *++** (top right) → **New repository** → name it `legalwithdev`
   → **Create repository**.
7. On the next page tap the link **"uploading an existing file"**.
8. Tap **"choose your files"** → select **all 7 files at once** from your
   extracted folder → wait for the upload bar to finish.
9. Tap green **Commit changes**.

### Part 3 — Render (about 10 minutes)
10. Go to **render.com** → **Get Started** → **Sign in with GitHub**
    (approve the permission pop-ups).
11. Dashboard → **New +** → **Web Service** → tap your `legalwithdev` repo →
    **Connect**.
12. Settings: **Name** = legalwithdev, **Region** = Singapore,
    **Instance Type** = **Free** → tap **Deploy Web Service**.
13. Wait 3–5 minutes (logs will show pip install...). When it turns green,
    your live link appears at the top: `https://legalwithdev.onrender.com`
    — **your chatbot is live!** Share it anywhere.

**Notes:** No credit card needed. After 15 idle minutes the bot sleeps;
the next visitor wakes it in ~30–50 seconds.

## Connecting an AI brain (optional but recommended)

The built-in knowledge base answers 10 topics. To answer ANY legal question
naturally, plug in a free AI API:

1. Render dashboard → your service → **Environment** → **Add Environment Variable**.
2. Add these three:
   - `AI_API_KEY` = your API key (e.g. free from console.groq.com)
   - `AI_BASE_URL` = `https://api.groq.com/openai/v1` (Groq) or
     `https://api.sarvam.ai/v1` (Sarvam AI)
   - `AI_MODEL` = `llama-3.3-70b-versatile` (Groq) or `sarvam-m` (Sarvam)
3. Also add `openai` to requirements.txt (remove the `#` on that line).
4. **Manual Deploy** → **Deploy latest commit**. Done.

## Adding the Telegram bot (optional)

1. In Telegram, message **@BotFather** → `/newbot` → copy the token.
2. Render → **New +** → **Background Worker** → same repo → **Connect**.
3. Start command: `python telegram_bot.py`, **Free** plan → Deploy.
4. Worker → **Environment** → add `TELEGRAM_BOT_TOKEN` = your token.
5. Redeploy. Now message your bot in Telegram — it replies!

## Adding legal topics

Open `indian_law_kb.json` — each topic has `keywords` (words users type),
`title`, `answer`, `sources`. Add a new block, commit the change on GitHub,
Render redeploys automatically.

## WhatsApp (later)

WhatsApp needs Meta business approval:
1. developers.facebook.com → Create App → add **WhatsApp** product.
2. Get token + phone number ID from the dashboard.
3. Render → your web service → Environment → add `WHATSAPP_TOKEN`,
   `WHATSAPP_PHONE_ID`, `WHATSAPP_VERIFY_TOKEN` (any secret word).
4. In Meta's WhatsApp → Configuration: Callback URL =
   `https://your-app.onrender.com/webhook/whatsapp`, verify token = the same
   secret word, subscribe to `messages`.
5. In `main.py`, inside `handle_whatsapp_message`, remove the `#` before
   `send_whatsapp_text(...)`, and in requirements.txt remove the `#` before
   `requests`. Commit → done.

## Responsible use

- Keep the "general information, not legal advice" disclaimer.
- Emergencies → police (100 / 112).
- Free legal aid → NALSA (nalsa.gov.in / 15100).
- Have a lawyer review answers before serving real users.

## Deploy log

- 23 Sep 2026: WhatsApp bot webhook (functions/webhook/whatsapp.js) live-deploy trigger (after 5f5621a).
