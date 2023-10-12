from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()

from utils import send_message


async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "view_list"

    # TODO: get list from database

    await send_message(update, context, "<tasks>")


async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "view_schedule"

    # TODO: get schedule from google calendar

    await send_message(update, context, "<schedule>")
