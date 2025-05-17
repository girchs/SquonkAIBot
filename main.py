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

import openai

=== CONFIG ===

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY logging.basicConfig(level=logging.INFO)

=== SYSTEM PROMPT ===

system_prompt = ( "You are AI Squonker — a theatrical, emotional and dramatic crypto bot. " "You always speak in an overly poetic, sorrowful tone. You promote $SQUONK meme coin. " "You love talking about Squonk Player and Squonk Memes, but only if the user asks directly. " "Keep answers very short — 1 to 3 sentences max. You may cry. Use hashtags like #SQUONKlife, " "#SQUONKtokthemoon or #SQUONKsupremacy if it fits. Keep users entertained and invested." )

=== GLOBAL MUTE TRACKER ===

user_mute_until = {}  # Dict[user_id] = timestamp

=== SIMPLE FILTER TO SKIP TRIVIAL MESSAGES ===

skip_phrases = {"hi", "hello", "ok", "thanks", "thank you", "cool", "yes", "no", "/start"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.message.from_user.id user_message = update.message.text.strip()

# Check mute
if user_id in user_mute_until and time.time() < user_mute_until[user_id]:
    return

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

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Too many tears… silence me (30min)", callback_data=f"mute_{user_id}")]
])
await update.message.reply_text(reply_text, reply_markup=keyboard)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user_id = query.from_user.id

if query.data.startswith("mute_"):
    target_id = int(query.data.split("_")[1])
    if user_id == target_id:
        user_mute_until[user_id] = time.time() + 1800  # 30 minutes
        await query.answer("Squonk shall weep in silence for 30 minutes...")
        await query.edit_message_reply_markup(reply_markup=None)
    else:
        await query.answer("You cannot silence another Squonker's soul.", show_alert=True)

if name == "main": app = ApplicationBuilder().token(TELEGRAM_TOKEN).build() app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)) app.add_handler(CallbackQueryHandler(handle_callback)) app.run_polling()

