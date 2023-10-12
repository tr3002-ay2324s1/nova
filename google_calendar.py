from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()

from utils import send_message


async def google_login(
    update: Update, context: ContextTypes.DEFAULT_TYPE, auth_url: str, state: str
):
    if context.chat_data is not None:
        context.chat_data["state"] = "google_login"

    keyboard = [
        [
            InlineKeyboardButton("Login", url=auth_url),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "Let's get started by setting up your Google Calendar 📅",
        reply_markup=reply_markup,
    )


async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "login_start"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="login_complete_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="login_complete_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update, context, "Have you signed in to google?", reply_markup=reply_markup
    )
