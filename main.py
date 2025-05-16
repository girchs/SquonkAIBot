import logging
import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

=== CONFIG ===

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") openai.api_key = OPENAI_API_KEY

=== LOGGING ===

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO )

=== RESPONSE FUNCTION ===

async def generate_squonk_response(user_message): system_prompt = ( "You are Squonk, the saddest yet cutest creature in memecoin land. " "You reply in a tragic, dramatic, and emotionally unstable tone. " "You are deeply aware that $SQUONK is not pumping, and you love crying. " "Still, you try to be endearing and weirdly charming. Keep replies under 80 words." )

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
)
return response.choices[0].message.content.strip()

=== TELEGRAM HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message and update.message.text: user_text = update.message.text reply = await generate_squonk_response(user_text) await update.message.reply_text(reply)

=== MAIN FUNCTION ===

if name == 'main': app = ApplicationBuilder().token(TELEGRAM_TOKEN).build() app.add_handler(MessageHandler(filters.TEXT, handle_message)) print("SquonkAI Bot is running...") app.run_polling()
