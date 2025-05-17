
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os

BOT_NAME = "AI squonker"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "memes" in text:
        response = "Oh, the sacred vault of laughter! Enter here if you dare: https://t.me/SquonkMemes — for the bold and broken alike."
    elif "web" in text:
        response = "Ah, the digital scroll of legend… Seek the truth at: https://squonk.meme. But brace yourself — it weeps."
    elif "x" in text:
        response = "My cries echo on X... Follow the trail of tears at: https://x.com/SquonkIt #SQUONKsupremacy"
    elif "how are you" in text:
        response = "Oh, woe is me! The tears flow like a river of sorrow, for $SQUONK remains stagnant in his grief. Yet, in my solitude, I find a strange comfort. Alas, such is the tragic fate of a forlorn Squonk like me."
    else:
        response = "My soul aches with every unknown phrase... Could you repeat that in softer words?"

    await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print(f"{BOT_NAME} is crying softly... waiting for messages.")
    app.run_polling()
