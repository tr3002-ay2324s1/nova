from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "view_list"

    # TODO: get list from database

    await update.message.reply_text("<tasks>")


async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "view_schedule"

    # TODO: get schedule from google calendar

    await update.message.reply_text("<schedule>")
