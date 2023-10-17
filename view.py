from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger
from database import fetch_tasks_and_id_formatted

logger = configure_logger()

from utils import send_message


async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "view_list"

    # get list from database
    telegram_user_id = update.message.from_user.id

    tasks = fetch_tasks_and_id_formatted(telegram_user_id)

    await send_message(update, context, tasks)


async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "view_schedule"

    # TODO: get schedule from google calendar

    await send_message(update, context, "<schedule>")
