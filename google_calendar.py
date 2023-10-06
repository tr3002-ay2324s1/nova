from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def google_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "google_login"

    keyboard = [
        [
            InlineKeyboardButton("Login ", callback_data="google_login"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Let's get started by setting up your Google Calendar 📅",
        reply_markup=reply_markup,
    )


async def login_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "login_complete"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="login_complete_yes"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(
        "Have you signed in?", reply_markup=reply_markup
    )
