from datetime import datetime, timedelta
from typing import List
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.api_handler import get_user
from lib.google_cal import (
    GoogleCalendarEventMinimum,
    get_calendar_events,
    get_google_cal_link,
    merge_events,
)
from utils.constants import NEW_YORK_TIMEZONE_INFO
from utils.datetime_utils import get_closest_week
from utils.logger_config import configure_logger
from utils.utils import (
    send_message,
    send_on_error_message,
    update_chat_data_state,
)

logger = configure_logger()


@update_chat_data_state
async def habit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for habit_title")
        await send_on_error_message(context)
        return

    context.chat_data["new_habit"] = dict()

    await send_message(
        update,
        context,
        "That's the spirit! What's this habit you want to build?",
    )


@update_chat_data_state
async def habit_repetition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Sounds amazing! How many times per week?",
    )


@update_chat_data_state
async def habit_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "And how long do you think this habit will take each time?\n\n(in mins!)",
    )


def calculate_free_blocks(
    merged_events: List[GoogleCalendarEventMinimum],
    day_start: datetime,
    day_end: datetime,
) -> List[timedelta]:
    """
    Calculate free time blocks in a day, given the merged events.
    """
    free_blocks = []
    previous_event_end = day_start

    for event in merged_events:
        # Calculate the free block between the previous event and the current event
        event_start = datetime.fromisoformat(
            event.get("start").get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO))
        )
        event_end = datetime.fromisoformat(
            event.get("end").get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO))
        )
        if event_start > previous_event_end:
            free_blocks.append(event_start - previous_event_end)
        previous_event_end = event_end

    # Check for a free block at the end of the day
    if previous_event_end < day_end:
        free_blocks.append(day_end - previous_event_end)

    return free_blocks


def rank_days(events: List[GoogleCalendarEventMinimum]) -> List[tuple]:
    """
    Rank days by the amount of free time available.
    """
    # Group events by day
    events_by_day = {}

    for event in events:
        event_start = datetime.fromisoformat(
            event.get("start").get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO))
        )
        day = event_start.date()
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    # Calculate free blocks for each day and sum their durations
    free_time_by_day = {}
    for day, day_events in events_by_day.items():
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        merged_day_events = [
            GoogleCalendarEventMinimum(
                start=e.get("start"),
                end=e.get("end"),
                summary=e.get("summary"),
            )
            for e in merge_events(day_events)
        ]
        free_blocks = calculate_free_blocks(merged_day_events, day_start, day_end)
        free_time_by_day[day] = sum(free_blocks, timedelta())

    # Sort days by the total free time
    ranked_days = sorted(
        free_time_by_day.items(), key=lambda item: item[1], reverse=True
    )

    return ranked_days


@update_chat_data_state
async def habit_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for task_creation")
        await send_on_error_message(context)
        return

    title: str = context.chat_data["new_habit"]["title"] or ""
    repetition: str = context.chat_data["new_habit"]["repetition"] or ""
    duration: str = context.chat_data["new_habit"]["duration"] or ""

    await send_message(
        update,
        context,
        "Let's get started immediately.",
    )

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    time_min, time_max = get_closest_week()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        k=150,
    )

    merged_events = merge_events(events)
    ranked_days = rank_days(
        [
            GoogleCalendarEventMinimum(
                start=e.get("start"),
                end=e.get("end"),
                summary=e.get("summary"),
            )
            for e in merged_events
        ]
    )

    logger.info(ranked_days)

    # TODO: pick slot in each day either at start of day (8am) or end of day (7pm). If not available then pick slot with most buffer time

    await send_message(
        update,
        context,
        "I have scheduled " + title + " for " + repetition + " days this week!",
    )

    keyboard = [
        [
            InlineKeyboardButton("Looks Good!", callback_data="habit_creation_confirm"),
        ],
        [
            InlineKeyboardButton("Edit", callback_data="habit_creation_edit"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # TODO: store slots
    await send_message(
        update,
        context,
        "<slots>",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def habit_schedule_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = get_google_cal_link((context.user_data or {}).get("telegram_user_id", None))

    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="habit_schedule_edit_yes", url=url
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
async def habit_schedule_updated(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: update cron jobs

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def habit_command_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: add new task to database

    # TODO: create new event on gcal

    if context.chat_data is not None:
        context.chat_data["new_habit"] = dict()

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END
