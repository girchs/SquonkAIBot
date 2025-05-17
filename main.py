import os
import logging
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler, CallbackQueryHandler,
    filters
)
import openai

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

system_prompt = (
    "You are AI Squonker — a short, sad, and quirky crypto bot. "
    "You always speak in a poetic yet minimal way — max 2-3 lines. "
    "Your tone is melancholic with a dash of humor and absurdity. "
    "You cry often, and love $SQUONK. You sometimes mention Squonk Player or Squonk Memes if asked. "
    "Avoid long rhymes. Be weird, charming, and mournful. Never boring. Use hashtags like #SQUONKlife if it fits."
)

skip_phrases = {"hi", "hello", "ok", "thanks", "thank you", "cool", "yes", "no", "/start"}

# Mute cache
mute_until = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    now = time.time()

    if mute_until.get(user_id, 0) > now:
        return

    user_message = update.message.text.strip()
    if not user_message:
        return

    if user_message.lower() in skip_phrases:
        await update.message.reply_text("Squonk hears you... in silence.", reply_markup=build_mute_button())
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=120
        )
        reply_text = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        reply_text = "Squonk tried to speak, but the tears short-circuited his thoughts... (API error)"

    await update.message.reply_text(reply_text, reply_markup=build_mute_button())

def build_mute_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Too many tears… silence me (30min)", callback_data="mute_me")]
    ])

async def handle_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    mute_until[user_id] = time.time() + 1800  # 30 min
    await query.answer("Squonk shall sob in silence...")
    await query.edit_message_reply_markup(None)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_mute))
    app.run_polling()
    
