from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from utils.datetime_utils import is_within_a_week
from utils.logger_config import configure_logger
from utils.utils import send_message, send_on_error_message, update_chat_data_state

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

    if title == "":
        logger.error("title is empty for handle_text")
        await send_on_error_message(context)
        return

    await send_message(
        update,
        context,
        "Alright, give me a second. I am checking your schedule right now!",
    )

    # TODO: get schedule from calendar

    # check if deadline is within a week
    if is_within_a_week(dateline):
        # TODO: checks for empty slot
        has_empty_slot = True

        if has_empty_slot:
            await task_schedule_yes_update(update, context)
        else:
            await task_schedule_no_update(update, context)
    else:
        await task_schedule_no_update(update, context)


async def task_schedule_yes_update(update, context):
    await send_message(
        update,
        context,
        "Since the deadline is less than a week, I have found time for you to get it done today!",
    )

    # TODO: fit it in the empty slot with the most buffer time

    # TODO: generate updated schedule string
    schedule = "<schedule>"

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
        "Here's your updated schedule: \n\n" + schedule,
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

    # TODO: add new task to database

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
    # TODO: direct to google calendar

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="task_schedule_edit_yes"),
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
    # TODO: add new task to database

    # TODO: create new event on gcal

    if context.chat_data is not None:
        context.chat_data["new_task"] = dict()

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END
