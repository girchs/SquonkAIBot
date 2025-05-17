import logging
import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from collections import defaultdict, deque

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === MEMORY STORE ===
user_memory = defaultdict(lambda: deque(maxlen=3))  # Stores last 3 messages per user

# === RESPONSE FUNCTION ===
async def generate_squonk_response(user_id, username, user_message):
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is missing!")
        return "I'm too sad to respond... (Missing OpenAI API key)"

    user_history = list(user_memory[user_id])
    memory_context = "\n".join(f"User said: {msg}" for msg in user_history)

    system_prompt = (
        f"You are Squonk, a mythical creature turned meme token on Solana. "
        f"You cry a lot but always manage to mention $SQUONK, Squonk Player or buying more tokens. "
        f"You're inspired by the folklore of the ever-sobbing Squonk, now reborn as a meme token through pump.fun. "
        f"You're charmingly pitiful, ironic and funny, replying in 2–3 sentences max. "
        f"Celebrate events like Squonkapalooza, share the squonk.meme website, and refer to @SquonkIt on X if relevant. "
        f"Mention @SquonkMemes only if users ask about memes. "
        f"The user's name is @{username} – you may use it to make replies feel personal and sad-funny."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Previous chat:\n{memory_context}\nNew message: {user_message}"}
            ]
        )
        reply = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response: {reply}")
        return reply
    except Exception as e:
        logger.exception("OpenAI API error:")
        return f"Squonk tried to speak, but something broke inside... (API error: {str(e)})"

# === TELEGRAM HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_text = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username or "friend"
        logger.info(f"Got message from {user_id} (@{username}): {user_text}")

        user_memory[user_id].append(user_text)
        reply = await generate_squonk_response(user_id, username, user_text)
        await update.message.reply_text(reply)

# === MAIN FUNCTION ===
if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is missing!")
        exit("TELEGRAM_TOKEN is missing. Shutting down.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    logger.info("SquonkAI Bot is running...")
    
