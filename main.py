import os
import logging
from datetime import datetime, timedelta

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

openai = OpenAI(api_key=OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)

system_prompt = (
    "You are AI Squonker — a theatrical, emotional and dramatic crypto bot. "
    "Always speak in a sorrowful, quirky, poetic tone with a twist of sadness and humor. "
    "Promote $SQUONK subtly. Never give long poems. Answer in 2–3 short, creative lines max. "
    "Never reply to everyone, only when addressed directly."
)

# === In-memory state ===
mute_until = {}
global_message_count = 0

def is_muted(user_id):
    return user_id in mute_until and datetime.now() < mute_until[user_id]

def mute_user(user_id, minutes=30):
    mute_until[user_id] = datetime.now() + timedelta(minutes=minutes)

def should_add_footer():
    global global_message_count
    global_message_count += 1
    return global_message_count % 2 == 0

# === Footer helper ===
def add_x_link_footer(text):
    footer = "\n\nFeeling generous? Click here: https://x.com/search?q=%24SQUONK&t=XM3ZXDCVQ19KUAU_EG75Og&s=09\nLike a Squonk post and help me stop crying… for 5 seconds."
    return f"{text}{footer}"

# === HANDLER: TEXT ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    if is_muted(user_id):
        return

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

        if should_add_footer():
            reply_text = add_x_link_footer(reply_text)

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        reply_text = "Squonk tried to speak, but the tears short-circuited his thoughts... (API error)"
        await update.message.reply_text(reply_text)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Too many tears… silence me (30min)", callback_data="mute_me")]
    ])

    await update.message.reply_text(reply_text, reply_markup=keyboard)

# === HANDLER: BUTTON ===
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "mute_me":
        mute_user(query.from_user.id)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Squonk will weep in silence... for 30 minutes.")

# === MAIN RUN ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
    
