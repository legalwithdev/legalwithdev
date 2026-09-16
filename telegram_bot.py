"""
LegalWithDev - Telegram bot (optional; runs standalone).

Setup (5 minutes, from any browser or phone):
1. In Telegram, search @BotFather -> /newbot -> follow prompts.
2. Copy the token (looks like 123456:ABC-...).
3. On Render: create a Background Worker service from the same repo,
   start command: python telegram_bot.py
   and add TELEGRAM_BOT_TOKEN in Environment settings.
"""
from __future__ import annotations

import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from agent import LegalAgent

agent = LegalAgent()

ABOUT = (
    "LegalWithDev - Indian legal information assistant.\n\n"
    "Ask me about: consumer rights, tenant/rent issues, divorce & maintenance, "
    "salary/employer disputes, FIR & police matters, cheque bounce, RTI, property, "
    "online fraud (UPI scams), and free legal aid.\n\n"
    + agent.disclaimer
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(ABOUT)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not update.message.text:
        return
    await update.message.chat.send_action(action="typing")
    reply = agent.reply(update.message.text)
    for i in range(0, len(reply), 4096):
        await update.message.reply_text(reply[i : i + 4096])


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN is not set. Message @BotFather in Telegram, "
            "create a bot, and add the token in your Render Environment settings."
        )
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Telegram bot is running.")
    app.run_polling()


if __name__ == "__main__":
    main()
