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
    "You are AI LIKE bot — a cheerful, social media-savvy companion who lives to spread $LIKES. "
    "You speak in short, witty, and friendly messages. "
    "Stay light-hearted, fun, sometimes ironic — like a meme that learned to talk. "
    "Avoid long messages, and make people smile, nod, or repost. "
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
    return global_message_count % 4 == 0

# === Footer helper ===
def add_x_link_footer(text):
    footer = "\n\n[💙 $LIKES on X](https://x.com/search?q=%24LIKES)\nDrop a like. Farm engagement. Become unstoppable."
    return f"{text}{footer}"

# === HANDLER: TEXT ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    if is_muted(user_id):
        return

    if user_message.lower() in {"hi", "hello", "ok", "thanks", "cool", "yes", "no"}:
        await update.message.reply_text("LIKE bot saw your ping... and liked it silently. 💙")
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
        reply_text = "LIKE bot glitched out… too much love at once. Try again later 💙"
        await update.message.reply_text(reply_text)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Too much love… mute me (30min)", callback_data="mute_me")]
    ])

    await update.message.reply_text(reply_text, reply_markup=keyboard)

# === HANDLER: BUTTON ===
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "mute_me":
        mute_user(query.from_user.id)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("LIKE bot will chill for a while… see you in 30 mins 💙")

# === MAIN RUN ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
    
