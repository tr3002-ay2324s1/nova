from datetime import datetime, time, timedelta
from typing import List, Optional
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from flows.night_flow import night_flow_review
from lib.api_handler import get_user, mark_task_as_not_added
from lib.google_cal import (
    GoogleCalendarEventMinimum,
    NovaEvent,
    add_calendar_item,
    get_block_properties,
    get_calendar_events,
    get_google_cal_link,
    get_readable_cal_event_str,
    merge_events,
)
from utils.constants import DAY_END_TIME, NEW_YORK_TIMEZONE_INFO
from utils.datetime_utils import (
    get_current_till_day_end_datetimes,
    get_day_start_end_datetimes,
)
from utils.get_name_time_from_job_name import get_name_time_from_job_name
from utils.job_queue import add_once_job
from utils.logger_config import configure_logger
from utils.update_cron_jobs import update_cron_jobs
from utils.utils import (
    send_message,
    send_on_error_message,
    update_chat_data_state,
    update_chat_data_state_context,
)

logger = configure_logger()


@update_chat_data_state_context
async def block_start_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.job is None:
        logger.error("context.job is None for block_alert")
        await send_on_error_message(context)
        return
    if context.job.name is None:
        logger.error("context.job.name is None for block_alert")
        await send_on_error_message(context)
        return
    if context.chat_data is None:
        logger.error("context.chat_data is None for block_alert")
        await send_on_error_message(context)
        return

    keyboard = [
        [
            InlineKeyboardButton("Ok!", callback_data="block_start_alert_confirm"),
        ],
        [
            InlineKeyboardButton(
                "Change of Plans",
                callback_data="block_flow_schedule_edit",
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    name, time = get_name_time_from_job_name(context.job.name)

    context.chat_data["job"] = dict()
    context.chat_data["job"]["name"] = name
    context.chat_data["job"]["time"] = time

    await send_message(
        None,
        context,
        "It's almost " + time[:2] + ":" + time[-2:] + ". Time to work on " + name,
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def block_start_alert_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for block_start_alert_confirm")
        await send_on_error_message(context)
        return

    name = context.chat_data["job"]["name"]

    # get block end time
    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""), q=name, k=1
    )
    if len(events) != 1:
        logger.error("Failed to find block")
        await send_on_error_message(context)
        return
    block = events[0]
    block_props = get_block_properties(block=block)
    nova_type = (block_props and block_props.get("nova_type", False)) or NovaEvent.TASK
      
    if nova_type == NovaEvent.TASK:
      # Only send follow-up if task.
      await add_once_job(
          callback=block_end_alert,
          when=(
              datetime.fromisoformat(
                  block.get("end").get(
                      "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
                  )
              )
          ),
          chat_id=context.chat_data["chat_id"],
          context=context,
          data=name,
      )

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def block_flow_schedule_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for block_flow_schedule_edit")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    url = get_google_cal_link(user_id)

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="block_flow_schedule_edit_yes"),
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
        "Have you edited?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def block_flow_schedule_updated(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    timeMin, timeMax = get_current_till_day_end_datetimes()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=timeMin.isoformat(),
        timeMax=timeMax.isoformat(),
        k=150,
    )
    schedule = get_readable_cal_event_str(events)

    await update_cron_jobs(context)

    await send_message(
        update,
        context,
        "Updated your schedule!\n\n" + schedule,
    )

    await block_next_alert(update, context)


@update_chat_data_state
async def block_next_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    timeMin, timeMax = get_current_till_day_end_datetimes()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=timeMin.isoformat(),
        timeMax=timeMax.isoformat(),
        k=150,
    )

    has_upcoming_block = len(events) != 0

    if has_upcoming_block:
        event = events[0]
        name = event.get("summary")
        start_time = (
            datetime.fromisoformat(
                event.get("start").get(
                    "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
                )
            ).strftime("%H:%M")
            or ""
        )
        await send_message(
            update,
            context,
            "Nice job! Next up you have " + name + " at " + start_time,
        )
    else:
        await night_flow_review(update, context)


@update_chat_data_state_context
async def block_end_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.job is None:
        logger.error("context.job is None for block_start_alert_confirm")
        await send_on_error_message(context)
        return
    if context.job.name is None:
        logger.error("context.job.name is None for block_start_alert_confirm")
        await send_on_error_message(context)
        return
    if context.chat_data is None:
        logger.error("context.chat_data is None for block_start_alert_confirm")
        await send_on_error_message(context)
        return

    name, time = get_name_time_from_job_name(context.job.name)

    context.chat_data["job"] = dict()
    context.chat_data["job"]["name"] = name
    context.chat_data["job"]["time"] = time

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="block_end_alert_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="block_end_alert_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        None,
        context,
        "Time's up! Did you get " + name + " done?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def block_end_alert_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "How much more time do you need? (in minutes)",
    )


def find_today_next_available_slot(
    events: List[GoogleCalendarEventMinimum],
    duration_str: str,
) -> Optional[time]:
    duration: timedelta = timedelta(minutes=int(duration_str))

    # merge events
    merged_events = merge_events(events)

    if (
        len(merged_events) == 0
        and (datetime.now(tz=NEW_YORK_TIMEZONE_INFO) + duration).time() <= DAY_END_TIME
    ):
        return datetime.now(tz=NEW_YORK_TIMEZONE_INFO).time()

    for i in range(len(merged_events)):
        if i < len(merged_events) - 1:
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
        else:
            start_of_buffer = datetime.fromisoformat(
                merged_events[i]
                .get("end")
                .get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat())
            )
            end_of_buffer = datetime.combine(
                datetime.now(tz=NEW_YORK_TIMEZONE_INFO).date(),
                DAY_END_TIME,
                tzinfo=NEW_YORK_TIMEZONE_INFO,
            )
        buffer_duration = end_of_buffer - start_of_buffer

        if buffer_duration >= duration:
            return start_of_buffer.time()

    return None


@update_chat_data_state
async def block_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for block_update")
        await send_on_error_message(context)
        return

    name = context.chat_data["job"]["name"]
    duration = context.chat_data["new_block"]["duration"]

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    timeMin, timeMax = get_current_till_day_end_datetimes()
    events_full = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=timeMin.isoformat(),
        timeMax=timeMax.isoformat(),
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

    today_next_available_slot = find_today_next_available_slot(events, duration)

    if today_next_available_slot is None:
        # Get block details from Google Calendar
        events = get_calendar_events(
            refresh_token=user.get("google_refresh_token", ""), q=name, k=1
        )
        if len(events) != 1:
            logger.error("Failed to find block")
            await send_on_error_message(context)
            return
        block = events[0]
        block_props = get_block_properties(block=block)
        nova_type = (block_props and block_props.get("nova_type", False)) or NovaEvent.TASK
        if nova_type == NovaEvent.TASK and block_props:
          # Update DB with new block details
          task_id = int(block_props.get("task_id", "0"))
          deadline: str = block_props.get("deadline", "")

          mark_task_as_not_added(task_id=task_id)
            
        return

    start_time = NEW_YORK_TIMEZONE_INFO.localize(
        datetime.combine(
            datetime.now(tz=NEW_YORK_TIMEZONE_INFO).date(),
            today_next_available_slot,
        )
    )
    end_time = NEW_YORK_TIMEZONE_INFO.localize(
        datetime.combine(
            datetime.now(tz=NEW_YORK_TIMEZONE_INFO).date(),
            today_next_available_slot,
        )
        + timedelta(minutes=int(duration))
    )

    context.chat_data["new_block"]["start_time"] = start_time.isoformat()
    context.chat_data["new_block"]["end_time"] = end_time.isoformat()

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    add_calendar_item(
        refresh_token=user.get("google_refresh_token", ""),
        summary=name,
        start_time=start_time,
        end_time=end_time,
        event_type=NovaEvent.EVENT,
    )

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="block_update_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="block_update_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "You have some time at "
        + today_next_available_slot.strftime("%H:%M")
        + ". Would you like to work on it then?",
        reply_markup=reply_markup,
    )
