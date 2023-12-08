from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.api_handler import get_user
from lib.google_cal import NovaEvent, add_calendar_item, get_calendar_events, get_google_cal_link, get_readable_cal_event_str
from utils.constants import NEW_YORK_TIMEZONE_INFO
from utils.datetime_utils import get_day_start_end_datetimes, get_input_day_start_end_datetimes
from utils.logger_config import configure_logger
from utils.utils import send_message, send_on_error_message, update_chat_data_state
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logger = configure_logger()


@update_chat_data_state
async def event_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_title")
        await send_on_error_message(context)
        return

    context.chat_data["new_event"] = dict()

    await send_message(
        update,
        context,
        "What would you like to name this event?",
    )


@update_chat_data_state
async def event_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "When is this event?\n\n(in MMDD format please!)",
    )


@update_chat_data_state
async def event_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What time does this event start?\n\n(eg. 1930)",
    )


@update_chat_data_state
async def event_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What time does this event end?\n\n(eg. 2030)",
    )


@update_chat_data_state
async def event_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    title: str = context.chat_data["new_event"]["title"] or ""
    date: str = context.chat_data["new_event"]["date"] or ""
    start_time_str: str = context.chat_data["new_event"]["start_time"] or ""
    end_time_str: str = context.chat_data["new_event"]["end_time"] or ""

    if title == "" or date == "" or start_time_str == "" or end_time_str == "":
        logger.error("title or date or start_time or end_time is empty for handle_text")
        await send_on_error_message(context)
        return

    start_time = datetime.strptime(
        str(datetime.now(tz=NEW_YORK_TIMEZONE_INFO).year) + date + start_time_str,
        "%Y%m%d%H%M",
    )

    # Convert to datetime object from date and end_time_str
    end_time = datetime.strptime(
        str(datetime.now(tz=NEW_YORK_TIMEZONE_INFO).year) + date + end_time_str,
        "%Y%m%d%H%M",
    )

    user = get_user(context.chat_data["chat_id"])
    google_refresh_token = user.get("google_refresh_token", "") 

    add_calendar_item(
        refresh_token=google_refresh_token,
        summary=title,
        start_time=start_time,
        end_time=end_time,
        event_type=NovaEvent.EVENT,
    )

    # check if this new event clashes with some other event
    time_min = start_time
    time_max = end_time

    events_in_same_time_period = get_calendar_events(
        refresh_token=google_refresh_token,
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
    )

    if len(events_in_same_time_period) > 0:
        # Clash flow
        cal_url = get_google_cal_link(context.chat_data["chat_id"])

        keyboard = [
            [
                InlineKeyboardButton("Yes, take me to my calendar", url=cal_url),
                InlineKeyboardButton("No", callback_data="event_creation_confirm"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(
            update,
            context,
            f"""Added! But there is a clash with an event that is already in your calendar. Would you like to de-conflict?""",
            reply_markup=reply_markup,
        )

    else:
        # No clash flow
        keyboard = [
            [
                InlineKeyboardButton("Looks Good!", callback_data="event_creation_confirm"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(
            update,
            context,
            f"""Got it! I have created an event for "{title}" on {start_time.strftime("%A, %B %d, %Y")} from {start_time.strftime("%I:%M %p")} to {end_time.strftime("%I:%M %p")}""",
            reply_markup=reply_markup,
        )


@update_chat_data_state
async def event_command_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_command_end")
        await send_on_error_message(context)
        return

    # title: str = (
    #     context.chat_data["new_event"]["title"] if context.chat_data is not None else ""
    # )
    # date_str: str = (
    #     context.chat_data["new_event"]["date"] if context.chat_data is not None else ""
    # )  # MMDD format

    # start_time_str: str = (
    #     context.chat_data["new_event"]["start_time"]
    #     if context.chat_data is not None
    #     else ""
    # )  # HHMM format

    # start_time = datetime.strptime(
    #     str(datetime.now(tz=NEW_YORK_TIMEZONE_INFO).year) + date_str + start_time_str,
    #     "%Y%m%d%H%M",
    # )

    # end_time_str: str = (
    #     context.chat_data["new_event"]["end_time"]
    #     if context.chat_data is not None
    #     else ""
    # )

    # # Convert to datetime object from date and end_time_str
    # end_time = datetime.strptime(
    #     str(datetime.now(tz=NEW_YORK_TIMEZONE_INFO).year) + date_str + end_time_str,
    #     "%Y%m%d%H%M",
    # )

    # if title == "" or date_str == "" or start_time_str == "" or end_time_str == "":
    #     logger.error("title or date or start_time or end_time is empty for handle_text")
    #     await send_on_error_message(context)
    #     return
    # user = get_user(context.chat_data["chat_id"])

    # add_calendar_item(
    #     refresh_token=user.get("google_refresh_token", ""),
    #     summary=title,
    #     start_time=start_time,
    #     end_time=end_time,
    #     event_type=NovaEvent.EVENT,
    # )

    # Do nothing here basically cause user is ok with this

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def event_command_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["new_event"] = dict()

    await send_message(
        update,
        context,
        "Canceled!",
    )

    return ConversationHandler.END
