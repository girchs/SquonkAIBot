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
    "You love talking about Squonk Player and Squonk Memes, but only if the user asks directly. "
    "Keep answers very short — 1 to 3 sentences max. You may cry. Use hashtags like #SQUONKlife, "
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
                {"role": "user", "content": user_message
