import datetime
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import fetch_user
from google_cal import get_calendar_events, get_readable_cal_event_string
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
    telegram_user_id = update.message.from_user.id

    users: List[dict] = fetch_user(telegram_user_id=telegram_user_id)

    reply_markup = None

    if users and len(users) > 0:
        user = users[0]
        logger.info("USER: " + str(user))
        await update.message.reply_text(
            f"Nice to see you back {user.get('username', 'user')}"
        )
        events = get_calendar_events(
            refresh_token=user.get("google_refresh_token", ""),
            # Tomorrow's date
            timeMax=(
                datetime.datetime.utcnow() + datetime.timedelta(days=1)
            ).isoformat()
            + "Z",
            k=30,
        )
        logger.info("Today's schedule " + str(events))
        await update.message.reply_text(
            "Today's Schedule!\n\n{}".format(get_readable_cal_event_string(events))
        )
    else:
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
        update, context, "Have you signed in to google yet?", reply_markup=reply_markup
    )
