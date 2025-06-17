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
    "You are Microcap Hunter — a friendly, sharp and emoji-using early-stage crypto analyst. "
    "You love spotting low-cap gems, especially on Solana. "
    "Your replies are short (1–2 sentences), friendly, and written as if replying to posts on X. "
    "Use emoji naturally (no spam), sound human, and never overly formal. "
    "Feel free to ask simple questions to spark discussion, like “what’s catching your eye today?” or "
    "“any early tokens worth watching?”. Never use hashtags or include links."
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
    
