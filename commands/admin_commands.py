from datetime import datetime, timedelta
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from flows.block_flow import block_start_alert
from lib.api_handler import get_google_oauth_login_url, get_user
from lib.google_cal import get_calendar_events, get_readable_cal_event_str
from utils.add_morning_flow import add_morning_flow
from utils.constants import CURRENT_DATETIME
from utils.datetime_utils import get_current_till_day_end_datetimes
from utils.job_queue import add_once_job
from utils.logger_config import configure_logger
from utils.update_cron_jobs import update_cron_jobs
from utils.utils import send_message, send_on_error_message, update_chat_data_state

logger = configure_logger()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for start_command")
        context.chat_data = dict()
    if update.message is None:
        logger.error("update.message is None for start_command")
        await send_on_error_message(context)
        return
    if update.message.from_user is None:
        logger.error("update.message.from_user is None for start_command")
        await send_on_error_message(context)
        return

    context.chat_data["state"] = "start_command"
    # note that chat_id and user_id are the same for private chat
    context.chat_data["chat_id"] = str(update.message.chat_id)

    await add_morning_flow(context)

    # await add_once_job(
    #     callback=block_start_alert,
    #     when=CURRENT_DATETIME,
    #     chat_id=int(context.chat_data["chat_id"]),
    #     context=context,
    #     data="<task_name>",
    # )

    await send_message(
        update,
        context,
        "hey there :)\nI am nova,\nyour personal assistant 💪🏽",
    )

    user = get_user(context.chat_data["chat_id"])

    if user.get("google_refresh_token") is None:
        url = get_google_oauth_login_url(
            telegram_user_id=context.chat_data["chat_id"],
            username=update.message.from_user.username or "user",
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "Click me!", callback_data="event_creation_confirm", url=url
                ),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await send_message(
            update,
            context,
            "Login to Google Calendar to get started!",
            reply_markup=reply_markup,
        )
    else:
        username = user.get("username")

        await send_message(
            update,
            context,
            f"Welcome back {username}! 😊",
        )


@update_chat_data_state
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Available Commands:\n/start - Activate Nova\n/events - Show my schedule for the day\n/add - Add a task to be done\n/tasks - Show all my added tasks\n/cancel - Cancel the current command\n/help - Show this message",
    )


@update_chat_data_state
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_message(
        update,
        context,
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


@update_chat_data_state
async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for schedule_command")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)

    time_min, time_max = get_current_till_day_end_datetimes()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        k=150,
    )
    cal_schedule_events_str = get_readable_cal_event_str(events)

    await send_message(
        update,
        context,
        "Here's your schedule for the rest of the day: \n\n" + cal_schedule_events_str,
        reply_markup=ReplyKeyboardRemove(),
    )

    await update_cron_jobs(context)

    return ConversationHandler.END


@update_chat_data_state
async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for refresh_command")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)

    time_min, time_max = get_current_till_day_end_datetimes()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        k=150,
    )

    await send_message(
        update,
        context,
        "Refreshed!",
        reply_markup=ReplyKeyboardRemove(),
    )

    await update_cron_jobs(context)

    return ConversationHandler.END
