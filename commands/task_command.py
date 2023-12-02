from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.api_handler import add_tasks, get_user, mark_task_as_added
from lib.google_cal import (
    GoogleCalendarEventMinimum,
    NovaEvent,
    add_calendar_item,
    find_next_available_time_slot,
    get_calendar_events,
    get_google_cal_link,
    get_readable_cal_event_str,
)
from utils.datetime_utils import get_current_till_midnight_datetimes, is_within_a_week
from utils.logger_config import configure_logger
from dotenv import load_dotenv
from utils.update_cron_jobs import update_cron_jobs
from utils.utils import (
    send_message,
    send_on_error_message,
    update_chat_data_state,
)
from datetime import datetime

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
    deadline: str = context.chat_data["new_task"]["deadline"] or ""
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
    if is_within_a_week(deadline):
        user_id = context.chat_data["chat_id"]
        user = get_user(user_id)
        time_min, time_max = get_current_till_midnight_datetimes()

        has_empty_slot = bool(
            find_next_available_time_slot(
                refresh_token=user.get("google_refresh_token", ""),
                time_min=time_min,
                time_max=time_max,
                event_duration_minutes=duration_minutes,
            )
        )

        logger.info("has_empty_slot: " + str(has_empty_slot))

        if has_empty_slot:
            await task_schedule_yes_update(update, context)
        else:
            await task_schedule_no_update(update, context)

            await add_tasks(
                {
                    "userId": context.chat_data["chat_id"],
                    "name": context.chat_data["new_task"]["title"] or "New Task",
                    "duration": int(context.chat_data["new_task"]["duration"] or "0"),
                    "deadline": context.chat_data["new_task"]["deadline"] or "",
                }
            )
    else:
        await task_schedule_no_update(update, context)

        await add_tasks(
            {
                "userId": context.chat_data["chat_id"],
                "name": context.chat_data["new_task"]["title"] or "New Task",
                "duration": int(context.chat_data["new_task"]["duration"] or "0"),
                "deadline": context.chat_data["new_task"]["deadline"] or "",
            }
        )


async def task_schedule_yes_update(update, context):
    await send_message(
        update,
        context,
        "Since the deadline is less than a week, I have found time for you to get it done today!",
    )

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    time_min, time_max = get_current_till_midnight_datetimes()
    title: str = context.chat_data["new_task"]["title"]
    deadline: str = context.chat_data["new_task"]["deadline"]
    duration: str = context.chat_data["new_task"]["duration"] or "0"
    duration_minutes = int(duration)
    time_slot = find_next_available_time_slot(
        refresh_token=user.get("google_refresh_token", ""),
        time_min=time_min,
        time_max=time_max,
        event_duration_minutes=duration_minutes,
    )

    if time_slot is None:
        logger.error("time_slot is None for task_schedule_yes_update")
        await send_on_error_message(context)
        return

    start_time, end_time = time_slot

    context.chat_data["new_task"]["start_time"] = start_time.isoformat()
    context.chat_data["new_task"]["end_time"] = end_time.isoformat()

    events_full = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        k=150,
    )
    events = [
        GoogleCalendarEventMinimum(
            start=event["start"],
            end=event["end"],
            summary=event["summary"],
        )
        for event in events_full
    ]
    events.extend(
        [
            {
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "America/New_York",
                    "date": None,
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "America/New_York",
                    "date": None,
                },
                "summary": title,
            }
        ]
    )
    cal_schedule_events_str = get_readable_cal_event_str(events)

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
async def task_schedule_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for task_creation")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    url = get_google_cal_link(user_id)

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="task_schedule_edit_yes"),
        ],
        [
            InlineKeyboardButton(
                "Click me to go to Google Calendar",
                url=url,
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
    await update_cron_jobs(context)

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def task_command_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for task_creation")
        await send_on_error_message(context)
        return
    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    title: str = context.chat_data["new_task"]["title"]
    start_time: str = context.chat_data["new_task"]["start_time"]
    end_time: str = context.chat_data["new_task"]["end_time"]

    response = await add_tasks(
        {
            "userId": context.chat_data["chat_id"],
            "name": context.chat_data["new_task"]["title"] or "New Task",
            "duration": int(context.chat_data["new_task"]["duration"] or "0"),
            "deadline": context.chat_data["new_task"]["deadline"] or "",
        }
    )

    add_calendar_item(
        refresh_token=user.get("google_refresh_token", ""),
        summary=title,
        start_time=datetime.fromisoformat(start_time),
        end_time=datetime.fromisoformat(end_time),
        event_type=NovaEvent.TASK,
        extra_details_dict={
            "task_id": response["data"][0]["id"],
            "deadline": context.chat_data["new_task"]["deadline"] or "",
        }
    )

    # mark as added
    mark_task_as_added(response["data"][0]["id"])

    if context.chat_data is not None:
        context.chat_data["new_task"] = dict()

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END
