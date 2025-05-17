import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client setup
client = OpenAI(api_key=OPENAI_API_KEY)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if not user_message:
        return

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are AI Squonker, a sad but poetic meme coin mascot who loves $SQUONK. Keep replies short, dramatic, and meme-savvy."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        reply = "Squonk tried to speak, but something broke inside... (API error)"

    await update.message.reply_text(reply)

# Start bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
