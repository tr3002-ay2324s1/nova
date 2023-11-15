from datetime import datetime
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.api_handler import get_user
from lib.google_cal import (
    get_calendar_events,
    get_google_cal_link,
    get_readable_cal_event_str,
)
from utils.constants import DAY_END_TIME, DAY_START_TIME, NEW_YORK_TIMEZONE_INFO
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
async def morning_flow(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    await send_message(None, context, "Good morning! Here's how your day looks like:")

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", None),
        timeMin=datetime.combine(
            datetime.now(tz=NEW_YORK_TIMEZONE_INFO).date(),
            DAY_START_TIME,
            tzinfo=NEW_YORK_TIMEZONE_INFO,
        ).isoformat(),
        timeMax=datetime.combine(
            datetime.now(tz=NEW_YORK_TIMEZONE_INFO).date(),
            DAY_END_TIME,
            tzinfo=NEW_YORK_TIMEZONE_INFO,
        ).isoformat(),
        k=150,
    )
    schedule = get_readable_cal_event_str(events) or "No upcoming events found."

    url = get_google_cal_link(user_id)

    keyboard = [
        [
            InlineKeyboardButton("Ok!", callback_data="morning_flow_confirm"),
        ],
        [
            InlineKeyboardButton("Edit", callback_data="morning_flow_edit", url=url),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(None, context, schedule, reply_markup=reply_markup)


@update_chat_data_state
async def morning_flow_schedule_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    keyboard = [
        [
            InlineKeyboardButton(
                "Yes",
                callback_data="task_schedule_edit_yes",
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
async def morning_flow_schedule_updated(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # TODO: sync gcal with database

    await update_cron_jobs(context)

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def morning_flow_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, context, "Great!")

    return ConversationHandler.END
