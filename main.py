
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import openai

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Recognized meme terms
KEYWORDS = {
    "lambo": "Ah, the Lambo dreams... If only my $SQUONK bags were as fast as that glorious machine! But soon, dear friend. Soon...",
    "lamborghini": "Ah, the Lambo dreams... If only my $SQUONK bags were as fast as that glorious machine! But soon, dear friend. Soon...",
    "wen lambo": "Ah, the Lambo dreams... If only my $SQUONK bags were as fast as that glorious machine! But soon, dear friend. Soon...",
}

# Handler function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    for keyword, response in KEYWORDS.items():
        if keyword in user_message:
            await update.message.reply_text(response)
            return

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a dramatic, emotional AI named Squonker who loves memes and $SQUONK."},
                {"role": "user", "content": update.message.text},
            ]
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        await update.message.reply_text("Squonk tried to speak, but something broke inside... (API error)")

# Bot startup
if __name__ == '__main__':
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
