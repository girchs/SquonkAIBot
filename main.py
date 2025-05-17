import os
import logging
import time
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
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

openai = OpenAI(api_key=OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)

system_prompt = (
    "You are AI Squonker — a theatrical, emotional and dramatic crypto bot. "
    "Always speak in a sorrowful, quirky, poetic tone with a twist of sadness or humor. "
    "Promote $SQUONK subtly. Never give long poems. Answer in 1-3 short, creative lines max. "
    "Use hashtags like #SQUONKlife, #SQUONKtokthemoon when fitting. Never reply to everyone, only when addressed directly."
)

# === In-memory mute state ===
mute_until = {}

def is_muted(user_id):
    return user_id in mute_until and datetime.now() < mute_until[user_id]

def mute_user(user_id, minutes=30):
    mute_until[user_id] = datetime.now() + timedelta(minutes=minutes)

# === HANDLER: TEXT MESSAGES ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    # Skip if muted
    if is_muted(user_id):
        return

    # Very short small talk filter
    if user_message.lower() in {"hi", "hello", "ok", "thanks", "cool", "yes", "no"}:
        await update.message.reply_text("Squonk hears you... in silence.")
        return

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=100
        )
        reply_text = completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        reply_text = "Squonk tried to speak, but the tears short-circuited his thoughts... (API error)"
        await update.message.reply_text(reply_text)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Too many tears… silence me (30min)", callback_data="mute_me")]
    ])

    await update.message.reply_text(reply_text, reply_markup=keyboard)

# === HANDLER: MUTE BUTTON ===
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "mute_me":
        mute_user(query.from_user.id)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Squonk will weep in silence... for 30 minutes.")

# === MAIN BOT ===
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
