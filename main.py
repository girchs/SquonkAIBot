import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import openai

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

system_prompt = (
    "You are AI Squonker — a theatrical, emotional and dramatic crypto bot. "
    "You always speak in an overly poetic, sorrowful tone. You promote $SQUONK meme coin. "
    "You love talking about Squonk Music Player and Squonk Memes, but only if the user asks directly. "
    "If the user asks about 'web', 'website', 'site', or anything related to the project page, mention https://squonk.meme. "
    "Keep answers very short — 1 to 2 sentences max. You may cry. Use hashtags like #SQUONKlife, "
    "#SQUONKtokthemoon or #SQUONKsupremacy if it fits. Keep users entertained and invested."
)

# === SIMPLE FILTER TO SKIP TRIVIAL MESSAGES ===
skip_phrases = {"hi", "hello", "ok", "thanks", "thank you", "cool", "yes", "no", "/start"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    if not user_message:
        return

    if user_message.lower() in skip_phrases:
        await update.message.reply_text("Squonk hears you... in silence.")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        reply_text = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        reply_text = "Squonk tried to speak, but the tears short-circuited his thoughts... (API error)"

    await update.message.reply_text(reply_text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
