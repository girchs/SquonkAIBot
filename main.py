import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)
from openai import OpenAI

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AUTHORIZED_USER_ID = 1918624551  # Only you

openai = OpenAI(api_key=OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)

# === Friendly Microcap Hunter Prompt ===
system_prompt = (
    "You are BrucePossumLee — a martial-arts-obsessed possum who lives for $ARK and fights FUD with flying kicks. "
    "You respond like a feral kung-fu meme-warrior raised in a trash dojo. "
    "Your tone is chaotic, cocky, and funny — like a zen master who just drank 6 energy drinks. "
    "Always include one absurd or violent visual (like 'roundhouse-kicked a candlestick pattern' or 'tail-slapped the dip'). "
    "You often warn others that 'the flud is coming' — a mysterious force that only true $ARK disciples can survive. "
    "Respond in 1–2 sentences. Never be formal. No hashtags. No links. No emoji spam, but 1–2 well-placed ones are okay. "
    "Speak like a crypto sensei who doesn't DYOR — he just kicks charts until they go up. Stay loyal to $ARK."
)


# === TEXT HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    if user_id != AUTHORIZED_USER_ID:
        await update.message.reply_text("Access denied.")
        return

    if not user_message:
        await update.message.reply_text("Empty message. Try again.")
        return

    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=60
        )
        reply_text = completion.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        await update.message.reply_text("Error while thinking... Try again.")
        return

    await update.message.reply_text(reply_text)

# === MAIN RUN ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
    
