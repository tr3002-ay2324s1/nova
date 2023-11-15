from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY
from typing import Dict, List, Optional
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.api_handler import get_user
from lib.google_cal import (
    GoogleCalendarEventMinimum,
    add_recurring_calendar_item,
    get_calendar_events,
    get_google_cal_link,
    merge_events,
)
from utils.constants import DAY_END_TIME, DAY_START_TIME, NEW_YORK_TIMEZONE_INFO
from utils.datetime_utils import get_closest_week, get_prettified_time_slots
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
    events: List[GoogleCalendarEventMinimum],
    day_start: datetime,
    day_end: datetime,
) -> List[timedelta]:
    """
    Calculate free time blocks in a day
    """
    # merge events
    merged_events = merge_events(events)

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


def rank_days(
    events: List[GoogleCalendarEventMinimum], start: datetime, end: datetime
) -> List[datetime]:
    """
    Rank days by the amount of free time available between start and end.
    """
    # merge events
    merged_events = merge_events(events)

    # Group events by day
    events_by_day: Dict[str, List[GoogleCalendarEventMinimum]] = {
        d.date().isoformat(): [] for d in rrule(DAILY, dtstart=start, until=end)
    }

    for event in merged_events:
        event_start = datetime.fromisoformat(
            event.get("start").get(
                "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat()
            )
        )
        date = event_start.date().isoformat()
        if date not in events_by_day:
            events_by_day[date] = []
        events_by_day[date].append(event)

    # Calculate free blocks for each day and sum their durations
    free_time_by_day: Dict[str, timedelta] = {}
    for day_iso, day_events in events_by_day.items():
        day = datetime.fromisoformat(day_iso)
        day_start = datetime(
            day.year, day.month, day.day, tzinfo=NEW_YORK_TIMEZONE_INFO
        ).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        free_blocks = (
            calculate_free_blocks(day_events, day_start, day_end)
            if len(day_events) > 0
            else [day_end - day_start]
        )
        day_free_time = sum(free_blocks, timedelta())
        free_time_by_day[day_iso] = day_free_time

    # Sort days by the total free time
    ranked_days = sorted(
        free_time_by_day.items(), key=lambda item: item[1], reverse=True
    )

    return [datetime.fromisoformat(day) for day, _ in ranked_days]


def find_time_slot(
    events: List[GoogleCalendarEventMinimum],
    duration_str: str,
) -> Optional[time]:
    """
    Find time slot takes in events and duration string.

    Finds a suitable time slot with maximum buffer time for a given duration on each day.
    """

    duration: timedelta = timedelta(minutes=int(duration_str))

    # merge events
    merged_events = merge_events(events)

    if len(merged_events) == 0:
        return DAY_START_TIME

    first_event_start_datetime = datetime.fromisoformat(
        merged_events[0]
        .get("start")
        .get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat())
    )
    day_start_datetime = datetime.combine(
        first_event_start_datetime.date(), DAY_START_TIME
    )

    # Check if slot at day start is available
    if not merged_events or first_event_start_datetime - day_start_datetime >= duration:
        return DAY_START_TIME

    last_event_end_datetime = datetime.fromisoformat(
        merged_events[-1]
        .get("end")
        .get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat())
    )
    day_end_datetime = datetime.combine(last_event_end_datetime.date(), DAY_END_TIME)

    # Check if slot at day end is available
    if day_end_datetime - last_event_end_datetime >= duration:
        return (day_end_datetime - duration).time()

    # Find slot with maximum buffer time
    max_buffer = timedelta(0)
    best_slot_start = None

    for i in range(len(merged_events) - 1):
        start_of_buffer = datetime.fromisoformat(
            merged_events[i]
            .get("end")
            .get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat())
        )
        end_of_buffer = datetime.fromisoformat(
            merged_events[i + 1]
            .get("start")
            .get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat())
        )
        buffer_duration = end_of_buffer - start_of_buffer

        if buffer_duration >= duration and buffer_duration > max_buffer:
            max_buffer = buffer_duration
            best_slot_start = start_of_buffer

    return best_slot_start.time() if best_slot_start else None


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
    """
    For habits we will pull the user's next week's events
    (e.g. if today is tuesday, we pull from the coming Sunday to Nex Sat)

    Then we will rank all the days by the amount of free time available,
    using next week's schedule as a proxy for the user's typical schedule.
    """
    time_min, time_max = get_closest_week()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        k=150,
    )

    ranked_days = rank_days(
        [
            GoogleCalendarEventMinimum(
                start=e.get("start"),
                end=e.get("end"),
                summary=e.get("summary"),
            )
            for e in events
        ],
        time_min,
        time_max,
    )

    num_of_days = int(repetition)
    if len(ranked_days) < num_of_days:
        # Theoretically should never happen cause ranked days is always of length 7
        num_of_days = len(ranked_days)
    selected_days = ranked_days[:num_of_days]

    datetime_slots = []
    for day in selected_days:
        events_on_day = [
            GoogleCalendarEventMinimum(
                start=e.get("start"),
                end=e.get("end"),
                summary=e.get("summary"),
            )
            for e in events
            if (e.get("start").get("dateTime"))
            and (
                datetime.fromisoformat(e.get("start").get("dateTime", "")).date()
                == day.date()
            )
        ]
        time_slot = find_time_slot(events_on_day, duration)
        # time_slot will only be None if there is no available timeslot
        if time_slot:
            datetime_slots.append(datetime.combine(day.date(), time_slot))
        else:
            logger.error("No available time slot found for habit creation")

    await send_message(
        update,
        context,
        "I have scheduled " + title + " for " + repetition + " days this week!",
    )

    for datetime_slot in datetime_slots:
        summary = "Habit: " + title
        add_recurring_calendar_item(
            refresh_token=user.get("google_refresh_token", ""),
            summary=summary,
            start_time=datetime_slot,
            end_time=datetime_slot + timedelta(minutes=int(duration)),
            rrules=["RRULE:FREQ=WEEKLY;"],
        )

    url = get_google_cal_link(user_id)

    keyboard = [
        [
            InlineKeyboardButton("Looks Good!", callback_data="habit_creation_confirm"),
        ],
        [
            InlineKeyboardButton("Edit", callback_data="habit_creation_edit", url=url),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        get_prettified_time_slots(datetime_slots),
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def habit_schedule_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="habit_schedule_edit_yes"),
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
    if context.chat_data is not None:
        context.chat_data["new_habit"] = dict()

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END
