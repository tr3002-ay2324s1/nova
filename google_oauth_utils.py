import datetime
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import fetch_user
from google_cal import (
    get_calendar_events,
    get_login_google,
    get_readable_cal_event_string,
)
from logger_config import configure_logger

logger = configure_logger()

from utils import send_message, send_on_error_message, update_chat_data_state


@update_chat_data_state
async def google_login(
    update: Update, context: ContextTypes.DEFAULT_TYPE, auth_url: str
):
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


@update_chat_data_state
async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.error("update.message is None for login_start")
        await send_on_error_message(context)
        return
    if update.message.from_user is None:
        logger.error("update.message.from_user is None for login_start")
        await send_on_error_message(context)
        return

    users = fetch_user(telegram_user_id=update.message.from_user.id)

    reply_markup = None

    if users and len(users) > 0:
        user = users[0]
        logger.info("USER: " + str(user))
        await send_message(
            update=update,
            context=context,
            text=f"Nice to see you back {user.get('username', 'user')}",
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
        no_events = "No events today!"
        if len(events) == 0:
            await send_message(update=update, context=context, text=no_events)
        else:
            logger.info("Today's schedule " + str(events))
            await send_message(
                update=update,
                context=context,
                text="Today's Schedule!\n\n{}".format(
                    get_readable_cal_event_string(events)
                ),
            )
    else:
        telegram_username = update.message.from_user.username
        url, state = await get_login_google(
            telegram_user_id=update.message.from_user.id,
            username=telegram_username or "",
        )
        await google_login(update, context, auth_url=url)
