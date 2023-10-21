from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import fetch_user
from google_cal import get_calendar_events

from logger_config import configure_logger

logger = configure_logger()

from utils import send_message, send_on_error_message, update_chat_data_state


@update_chat_data_state
async def night_flow_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="night_flow_review_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="night_flow_review_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "That's the end of your work day! Would you like to review now?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def night_flow_feeling(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await send_message(
        update, context, "Today you completed tasks <a>, <b>, <c>. How are you feeling?"
    )


@update_chat_data_state
async def night_flow_favourite(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await send_message(update, context, "What was your favourite part of the day?")


@update_chat_data_state
async def night_flow_proud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(update, context, "What are you proud of yourself for today?")


@update_chat_data_state
async def night_flow_improve(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await send_message(update, context, "What was one thing you can improve on?")


@update_chat_data_state
async def night_flow_next_day_schedule(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        logger.error("update.message is None for night_flow_next_day_schedule")
        await send_on_error_message(context)
        return
    if update.message.from_user is None:
        logger.error(
            "update.message.from_user is None for night_flow_next_day_schedule"
        )
        await send_on_error_message(context)
        return

    users = fetch_user(telegram_user_id=update.message.from_user.id)
    first_user = users[0]
    refresh_token = first_user.get("google_refresh_token", "")
    # Get events from tomorrow 12am to tomorrow 11:59pm
    today = datetime.utcnow()
    today_midnight = datetime(today.year, today.month, today.day, 0, 0)
    events = get_calendar_events(
        refresh_token=refresh_token,
        timeMin=today_midnight.isoformat() + "Z",
        timeMax=(today_midnight + timedelta(days=1)).isoformat() + "Z",
        k=20,
    )

    event_str = "".join(
        [
            f"{e.get('summary', '')} at {e.get('start', {}).get('dateTime', '')}\n"
            for e in events
        ]
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "Ok!", callback_data="night_flow_next_day_schedule_ok"
            ),
        ],
        [
            InlineKeyboardButton(
                "Edit", callback_data="night_flow_next_day_schedule_edit"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update, context, "Here's your schedule for tomorrow!")

    await send_message(update, context, event_str, reply_markup=reply_markup)


@update_chat_data_state
async def night_flow_pick_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await send_message(
        update,
        context,
        "Pick a time to review later (answer in 24h format e.g. 1800 for 6pm)",
    )


@update_chat_data_state
async def night_flow_invalid_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await send_message(
        update,
        context,
        "Invalid Time! Please try again. (answer in 24h format e.g. 1800 for 6pm)",
    )


@update_chat_data_state
async def night_flow_new_review_time(context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="night_flow_new_review_time_yes"),
        ],
        [
            InlineKeyboardButton(
                "Skip", callback_data="night_flow_new_review_time_skip"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        None, context, "It is time to review your day!", reply_markup=reply_markup
    )


@update_chat_data_state
async def night_flow_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(
        update, context, "Alright, let's get straight to planning for tomorrow then!"
    )

    await night_flow_next_day_schedule(update, context)


@update_chat_data_state
async def night_flow_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, context, "Good night!")

    return ConversationHandler.END


@update_chat_data_state
async def night_flow_next_day_schedule_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="night_flow_next_day_schedule_edit_yes"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update, context, "Have you edited?", reply_markup=reply_markup)
