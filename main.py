import os
import time
import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from openai import OpenAI

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)

# === MAIN LOGIC ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a poetic Squonk bot promoting $SQUONK."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=150
        )

        reply_text = completion.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        reply_text = "Squonk tried to speak, but the tears short-circuited his thoughts... (API error)"

    await update.message.reply_text(reply_text)

# === INIT ===

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
    
