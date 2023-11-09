import pytz
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.api_handler import add_tasks, get_user
from lib.google_cal import (
    NovaEvent,
    add_calendar_item,
    find_next_available_time_slot,
    get_calendar_events,
    get_google_cal_link,
    get_readable_cal_event_str,
)
from utils.constants import NEW_YORK_TIMEZONE_INFO
from utils.datetime_utils import get_datetimes_till_end_of_day, is_within_a_week
from utils.logger_config import configure_logger
from dotenv import load_dotenv
import requests
import os
from utils.utils import (
    send_message,
    send_on_error_message,
    update_chat_data_state,
)
from datetime import datetime, timedelta

load_dotenv()
logger = configure_logger()


@update_chat_data_state
async def task_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for task_title")
        await send_on_error_message(context)
        return

    context.chat_data["new_task"] = dict()

    await send_message(
        update,
        context,
        "Cool! What is this task on your mind?",
    )


@update_chat_data_state
async def task_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Got it! When should this be completed by?\n\n(MMDD format please!)",
    )


@update_chat_data_state
async def task_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Noted! About how long do you think it'll take you to complete this task?\n\n(in mins!)",
    )


@update_chat_data_state
async def task_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for task_creation")
        await send_on_error_message(context)
        return

    title: str = context.chat_data["new_task"]["title"] or ""
    dateline: str = context.chat_data["new_task"]["dateline"] or ""
    duration: str = context.chat_data["new_task"]["duration"] or "0"

    duration_minutes = int(duration)

    if title == "":
        logger.error("title is empty for handle_text")
        await send_on_error_message(context)
        return

    await send_message(
        update,
        context,
        "Alright, give me a second. I am checking your schedule right now!",
    )

    # check if deadline is within a week
    if is_within_a_week(dateline):
        user_id = context.chat_data["chat_id"]
        user = get_user(user_id)
        time_min, time_max = get_datetimes_till_end_of_day()

        has_empty_slot = bool(
            await find_next_available_time_slot(
                refresh_token=user.get("google_refresh_token", ""),
                time_min=time_min,
                time_max=time_max,
                event_duration_minutes=duration_minutes,
            )
        )

        if has_empty_slot:
            await task_schedule_yes_update(update, context)
        else:
            await task_schedule_no_update(update, context)

        add_tasks(
            [
                {
                    "userId": context.chat_data["chat_id"],
                    "name": context.chat_data["new_task"]["title"] or "New Task",
                    "duration": int(context.chat_data["new_task"]["duration"] or "0"),
                    "deadline": context.chat_data["new_task"]["dateline"] or "",
                }
            ]
        )
    else:
        await task_schedule_no_update(update, context)
        add_tasks(
            [
                {
                    "userId": context.chat_data["chat_id"],
                    "name": context.chat_data["new_task"]["title"] or "New Task",
                    "duration": int(context.chat_data["new_task"]["duration"] or "0"),
                    "deadline": context.chat_data["new_task"]["dateline"] or "",
                }
            ]
        )


async def task_schedule_yes_update(update, context):
    await send_message(
        update,
        context,
        "Since the deadline is less than a week, I have found time for you to get it done today!",
    )

    user = get_user(context.chat_data["chat_id"])
    time_min, time_max = get_datetimes_till_end_of_day()
    duration: str = context.chat_data["new_task"]["duration"] or "0"
    duration_minutes = int(duration)
    time_slot = await find_next_available_time_slot(
        refresh_token=user.get("google_refresh_token", ""),
        time_min=time_min,
        time_max=time_max,
        event_duration_minutes=duration_minutes,
    )

    if not time_slot:
        logger.error("time_slot is empty for task_schedule_yes_update")
        await send_on_error_message(context)
        return

    start_time, end_time = time_slot

    add_calendar_item(
        refresh_token=user.get("google_refresh_token", ""),
        summary=context.chat_data["new_task"]["title"] or "New Task",
        start_time=start_time,
        end_time=end_time,
        event_type=NovaEvent.TASK,
    )

    cal_schedule_events_str = get_readable_cal_event_str(
        get_calendar_events(
            refresh_token=user.get("google_refresh_token", None),
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            k=15,
        )
    )

    keyboard = [
        [
            InlineKeyboardButton("Looks Good!", callback_data="task_creation_confirm"),
        ],
        [
            InlineKeyboardButton("Edit", callback_data="task_creation_edit"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "Here's your updated schedule: \n\n" + cal_schedule_events_str,
        reply_markup=reply_markup,
    )


async def task_schedule_no_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for task_creation")
        await send_on_error_message(context)
        return

    title: str = context.chat_data["new_task"]["title"] or ""

    if title == "":
        logger.error("title is empty for handle_text")
        await send_on_error_message(context)
        return

    await send_message(
        update,
        context,
        'No changes to today’s schedule!\n\nI have added your task "'
        + title
        + '" into your list!',
    )


@update_chat_data_state
async def task_creation_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Have you edited your calendar?",
    )


@update_chat_data_state
async def task_schedule_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = get_google_cal_link((context.user_data or {}).get("telegram_user_id", None))

    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="task_schedule_edit_yes", url=url
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "Have you edited your calendar?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def task_schedule_updated(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: update cron jobs

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def task_command_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Get event/task/habit data
    add_calendar_item(
        refresh_token=(context.user_data or {}).get("google_refresh_token", None),
        summary="test",  # TODO: REPLACE
        start_time=datetime.now(tz=NEW_YORK_TIMEZONE_INFO),  # TODO: REPLACE
        end_time=datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
        + timedelta(minutes=30),  # TODO: REPLACE
        event_type=NovaEvent.TASK,  # TODO: REPLACE
    )

    if context.chat_data is not None:
        context.chat_data["new_task"] = dict()

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END
