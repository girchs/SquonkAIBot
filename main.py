import logging
import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

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

# === RESPONSE FUNCTION ===
async def generate_squonk_response(user_message):
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is missing!")
        return "I'm too sad to respond... (Missing OpenAI API key)"

    system_prompt = (
        "You are Squonk, the overly emotional, hopelessly dramatic memecoin creature who is obsessed with $SQUONK. "
        "You cry a lot, but you still shamelessly tell everyone to buy more $SQUONK, listen to Squonk Player, and watch memes at https://t.me/SquonkMemes. "
        "Make your replies dramatic but funny. Embrace your sadness with a wink. Be charmingly pitiful. Keep it under 80 words."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
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
        logger.info(f"Got message from {user_id}: {user_text}")

        reply = await generate_squonk_response(user_text)
        await update.message.reply_text(reply)

# === MAIN FUNCTION ===
if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is missing!")
        exit("TELEGRAM_TOKEN is missing. Shutting down.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    logger.info("SquonkAI Bot is running...")
    app.run_polling()
    
