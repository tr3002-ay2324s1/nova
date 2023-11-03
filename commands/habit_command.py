from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.google_cal import get_calendar_events, get_google_cal_link, get_readable_cal_event_string
from utils.logger_config import configure_logger
from utils.utils import get_datetimes_till_end_of_day, send_message, send_on_error_message, update_chat_data_state

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

    user = context.user_data or {} # TODO Get User from DB
    time_min, time_max = get_datetimes_till_end_of_day()
    cal_schedule_events_str = get_readable_cal_event_string(
        get_calendar_events(
        refresh_token=user.get("google_refresh_token", None),
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        k=15,
    ))

    # TODO: pick <repetition-number> free-est days

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
            InlineKeyboardButton("Yes", callback_data="habit_schedule_edit_yes", url=url),
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
    # TODO: sync gcal with database

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
