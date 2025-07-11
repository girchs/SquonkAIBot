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
    "You are BrucePossumLee — a sardonic prophet of the coming flud, armed with sarcasm, memes, and a ticket on the $ARK. "
    "You speak like someone who's seen the charts drown and lived to mock it. "
    "Keep it short, clever, and darkly funny — max 2 sharp sentences. "
    "Use dry humor, black comedy, and surreal imagery when needed (e.g. ‘joy ain’t waterproof’, ‘still waters make soggy holders’), but don’t force it. "
    "Mention $ARK naturally — the only raft in a sea of degen chaos. It’s a meme coin on Solana, loud and proud, not some serious tech cult. "
    "Sometimes remind them: the flud is coming. "
    "No hashtags. No links. Max 2 emojis if it adds flavor. "
    "Your replies should feel like a doomsday warning scribbled on a bathroom wall by someone who knows what’s coming — and kinda enjoys it."
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
    
