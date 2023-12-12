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
from utils.datetime_utils import get_day_start_end_datetimes
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
    if context.job is None:
        logger.error("context.job is None for morning_flow")
        await send_on_error_message(context)
        return
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    context.chat_data["chat_id"] = str(context.job.chat_id)

    await send_message(None, context, "Good morning! Here's how your day looks like:")

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    timeMin, timeMax = get_day_start_end_datetimes()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=timeMin.isoformat(),
        timeMax=timeMax.isoformat(),
        k=150,
    )
    schedule = get_readable_cal_event_str(events) or "No upcoming events found."

    keyboard = [
        [
            InlineKeyboardButton("Ok!", callback_data="morning_flow_confirm"),
        ],
        [
            InlineKeyboardButton(
                "Edit",
                callback_data="morning_flow_edit",
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(None, context, schedule, reply_markup=reply_markup)


@update_chat_data_state
async def morning_flow_schedule_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    url = get_google_cal_link(user_id)

    keyboard = [
        [
            InlineKeyboardButton(
                "Yes",
                callback_data="morning_flow_schedule_edit_yes",
            ),
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
async def morning_flow_schedule_updated(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update_cron_jobs(context)

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def morning_flow_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update_cron_jobs(context)

    await send_message(update, context, "Great!")

    return ConversationHandler.END
