from datetime import datetime, timedelta
from math import ceil
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import fetch_user
from google_cal import (
    find_next_available_time_slot,
    get_calendar_events,
    get_readable_cal_event_string,
    refresh_daily_jobs_with_google_cal,
)

from logger_config import configure_logger

logger = configure_logger()

from utils import send_message, send_on_error_message, update_chat_data_state, update_chat_data_state_context

from night_flow import night_flow_review


@update_chat_data_state_context
async def morning_flow_greeting(context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(None, context, "Good morning! Here's how your day looks like:")

    await morning_flow_schedule(context)


@update_chat_data_state_context
async def morning_flow_schedule(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for morning_flow_events")
        await send_on_error_message(context)
        return

    events = await refresh_daily_jobs_with_google_cal(
        context=context,
        get_next_event_job=morning_flow_event,
    )

    event_str = get_readable_cal_event_string(events)

    keyboard = [
        [
            InlineKeyboardButton(
                "Looks Good!", callback_data="morning_flow_schedule_acknowledge"
            ),
        ],
        [
            InlineKeyboardButton("Edit", callback_data="morning_flow_schedule_edit"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(None, context, str(event_str), reply_markup=reply_markup)


@update_chat_data_state
async def morning_flow_schedule_edit_acknowledge(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="morning_flow_schedule_acknowledge"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update, context, "Have you edited", reply_markup=reply_markup)


def morning_flow_event(
    time_of_event: datetime, event_desc: str, end_time_of_event: Optional[datetime]
):  # -> Callable[..., Coroutine[Any, Any, None]]:
    @update_chat_data_state_context
    async def morning_flow_event_helper(context: ContextTypes.DEFAULT_TYPE) -> None:
        if context.chat_data is None or not context.chat_data:
            logger.error("context.chat_data is None for morning_flow_event_helper")
            await send_on_error_message(context)
            return
        context.chat_data["state"] = end_time_of_event and end_time_of_event.isoformat()
        keyboard = [
            [
                InlineKeyboardButton("Ok!", callback_data="event_flow_acknowledge"),
            ],
            [
                InlineKeyboardButton(
                    "Change of Plans", callback_data="event_flow_edit"
                ),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await send_message(
            None,
            context,
            f"It's almost {time_of_event.isoformat()}. Time to work on the {event_desc}!",
            reply_markup=reply_markup,
        )

    return morning_flow_event_helper


@update_chat_data_state
async def event_flow_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="event_flow_edit_acknowledge_yes"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update, context, "Have you edited?", reply_markup=reply_markup)


@update_chat_data_state
async def direct_to_google_calendar(
    update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str
) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "Google Calendar",
                url="https://calendar.google.com/",
                callback_data=callback_data,
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update, context, "Go to", reply_markup=reply_markup)


@update_chat_data_state
async def morning_flow_event_update(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await morning_flow_check_next_task(update, context)


@update_chat_data_state
async def morning_flow_event_end(context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="morning_flow_event_end_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="morning_flow_event_end_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        None,
        context,
        "How was your deep work session? Did you get it done?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def morning_flow_next_event(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await morning_flow_check_next_task(update, context)


@update_chat_data_state
async def event_flow_reschedule(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if context.chat_data is None or not context.chat_data["user_id"]:
        logger.error("context.chat_data is None for event_flow_reschedule")
        await send_on_error_message(context)
        return
    end_datetime = datetime.fromisoformat(context.chat_data["state"])

    user_id = context.chat_data["user_id"]
    users = fetch_user(telegram_user_id=user_id)
    user = users[0]
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMax=(datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        k=1,
    )
    time_slot = await find_next_available_time_slot(
        refresh_token=user.get("google_refresh_token", ""),
        events=events,
        event_duration_minutes=ceil(
            (end_datetime - datetime.utcnow()).total_seconds() // 60
        ),
    )
    if time_slot is None:
        await send_message(
            update,
            context,
            "Looks like you have no time to reschedule to today :( Try again tomorrow!",
        )
        return
    time_slot_str = time_slot.strftime("%I:%M%p")
    context.chat_data["state"] = time_slot.isoformat()
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="morning_flow_new_task_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="morning_flow_new_task_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        f"You have some time at {time_slot_str}. Would you like to work on it then?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def morning_flow_check_next_task(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for morning_flow_check_next_task")
        await send_on_error_message(context)
        return
    if update.message is None:
        logger.error("update.message is None for morning_flow_check_next_task")
        await send_on_error_message(context)
        return
    if update.message.from_user is None:
        logger.error(
            "update.message.from_user is None for morning_flow_check_next_task"
        )
        await send_on_error_message(context)
        return

    users = fetch_user(
        telegram_user_id=update.message.from_user.id or context.chat_data["user_id"]
    )
    user = users[0]
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMax=(datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        k=1,
    )
    event_str = get_readable_cal_event_string(events)
    if event_str:
        await send_message(
            update,
            context,
            f"You have {event_str} next!",
        )
    else:
        await night_flow_review(update, context)
