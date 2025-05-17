import os
import time
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)
from openai import OpenAI

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)

system_prompt = (
    "You are AI Squonker — a theatrical, emotional and dramatic crypto bot. "
    "You always speak in an overly poetic, sorrowful tone. You promote $SQUONK meme coin. "
    "Keep responses very short — 1 to 3 sentences max. You may cry. "
    "Use hashtags like #SQUONKlife, #SQUONKtokthemoon, #SQUONKsupremacy if it fits. "
    "Mention Squonk Player or Squonk Memes only if asked directly."
)

# === MUTE TRACKER ===
user_mute_until = {}

# === MUTE CALLBACK ===
async def mute_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_mute_until[user_id] = time.time() + 30 * 60
    await query.answer("You won't hear my tears for 30 minutes...")
    await query.edit_message_reply_markup(reply_markup=None)

# === HANDLE MESSAGE ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    message = update.message.text.strip()

    if user_id in user_mute_until and time.time() < user_mute_until[user_id]:
        return

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=120
        )
        reply_text = completion.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        reply_text = "Squonk tried to speak, but the tears short-circuited his thoughts... (API error)"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Too many tears… silence me (30min)", callback_data="mute_me")]
    ])

    await update.message.reply_text(reply_text, reply_markup=keyboard)

# === MAIN ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CallbackQueryHandler(mute_callback, pattern="^mute_me$"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
        
