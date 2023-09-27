from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        update.message.text
        + " is not a valid command. Please use /start to start again."
    )


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        update.message.text + " is not a valid text. Please use /start to start again."
    )
