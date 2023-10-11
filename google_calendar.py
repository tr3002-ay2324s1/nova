from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def google_login(
    update: Update, context: ContextTypes.DEFAULT_TYPE, auth_url: str, state: str
):
    if not update.callback_query or not update.callback_query.message or not context.chat_data:
        print("google_login: update.message or context.chat_data is None")
        return
    context.chat_data["state"] = "google_login"

    keyboard = [
        [
            InlineKeyboardButton("Login", url=auth_url),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(
        "Let's get started by setting up your Google Calendar 📅",
        reply_markup=reply_markup,
    )


async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    await update.message.reply_text(
        "Have you signed in to google?", reply_markup=reply_markup
    )
