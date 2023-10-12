from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()

from utils import send_message


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is not None and update.message.text is not None:
        await send_message(
            update,
            context,
            update.message.text
            + " is not a valid command. Please use /start to start again.",
        )


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is not None and update.message.text is not None:
        await send_message(
            update,
            context,
            update.message.text
            + " is not a valid text. Please use /start to start again.",
        )
