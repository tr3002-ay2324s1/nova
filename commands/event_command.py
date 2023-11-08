from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from utils.logger_config import configure_logger
from utils.utils import send_message, send_on_error_message, update_chat_data_state
from dotenv import load_dotenv
import requests
import os

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
    start_time: str = context.chat_data["new_event"]["start_time"] or ""
    end_time: str = context.chat_data["new_event"]["end_time"] or ""

    if title == "" or date == "" or start_time == "" or end_time == "":
        logger.error("title or date or start_time or end_time is empty for handle_text")
        await send_on_error_message(context)
        return

    keyboard = [
        [
            InlineKeyboardButton("Looks Good!", callback_data="event_creation_confirm"),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data="event_creation_cancel"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        'Got it! I have created an event for "'
        + title
        + '" on '
        + date[:2]
        + "/"
        + date[-2:]
        + " from "
        + start_time
        + " to "
        + end_time,
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def event_command_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title: str = (
        context.chat_data["new_event"]["title"] if context.chat_data is not None else ""
    )
    date: str = (
        context.chat_data["new_event"]["date"] if context.chat_data is not None else ""
    )
    start_time: str = (
        context.chat_data["new_event"]["start_time"]
        if context.chat_data is not None
        else ""
    )
    end_time: str = (
        context.chat_data["new_event"]["end_time"]
        if context.chat_data is not None
        else ""
    )

    if title == "" or date == "" or start_time == "" or end_time == "":
        logger.error("title or date or start_time or end_time is empty for handle_text")
        await send_on_error_message(context)
        return

    data = {
        "userId": 123,
        "name": title,
        "description": "",
    }

    url_post = f"{os.getenv('REQUEST_URL')}/tasks"
    requests.post(url_post, json=data)

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
