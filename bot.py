import logging
from telegram.ext import ApplicationBuilder
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from utils import send_msg
from dotenv import load_dotenv
import os
# Load environment variables from the .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"I'm a bot, please talk to me!")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_chat.id)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Notify that the bot is awake
    send_msg("I'm awake!")

    # Add handlers for commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('getid', get_id))

    application.run_polling()