from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from google_cal import get_calendar_events, get_readable_cal_event_string
from utils import send_message, send_on_error_message, update_chat_data_state
from logger_config import configure_logger
from database import fetch_tasks_and_id_formatted, fetch_user

logger = configure_logger()


@update_chat_data_state
async def view_all_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.error("update.message is None for view_all_tasks")
        await send_on_error_message(context)
        return
    if update.message.from_user is None:
        logger.error("update.message.from_user is None for view_all_tasks")
        await send_on_error_message(context)
        return

    # get list from database
    telegram_user_id = update.message.from_user.id

    tasks = fetch_tasks_and_id_formatted(telegram_user_id)

    await send_message(update, context, tasks)


@update_chat_data_state
async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for view_schedule")
        await send_on_error_message(context)
        return
    if update.message is None:
        logger.error("update.message is None for view_schedule")
        await send_on_error_message(context)
        return
    if update.message.from_user is None:
        logger.error("update.message.from_user is None for view_schedule")
        await send_on_error_message(context)
        return

    users = fetch_user(
        telegram_user_id=update.message.from_user.id or context.chat_data["user_id"]
    )
    user = users[0]
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMax=(datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        k=30,
    )
    event_str = get_readable_cal_event_string(events)

    await send_message(update, context, event_str)
