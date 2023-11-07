from decimal import Context
from sqlalchemy import update
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from utils.logger_config import configure_logger
from utils.utils import (
    send_message,
    send_on_error_message,
    update_chat_data_state,
    update_chat_data_state_context,
)

logger = configure_logger()


@update_chat_data_state
async def night_flow_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="night_flow_review_yes"),
        ],
        [
            InlineKeyboardButton("Skip", callback_data="night_flow_review_skip"),
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
async def night_flow_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: get schedule from calendar
    schedule = ""

    await send_message(
        update,
        context,
        "Today you:\n" + schedule,
    )

    await night_flow_feeling(update, context)


@update_chat_data_state
async def night_flow_feeling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "How are you feeling?",
    )


@update_chat_data_state
async def night_flow_favourite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What was your favourite part of the day?",
    )


@update_chat_data_state
async def night_flow_proud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What are you proud of yourself for today?",
    )


@update_chat_data_state
async def night_flow_improve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What was one thing you can improve on?",
    )


@update_chat_data_state
async def night_flow_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Anything else you want to record for today?",
    )


@update_chat_data_state
async def night_flow_review_complete(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    feeling: str = context.chat_data["night_flow_review"]["feeling"] or ""
    favourite: str = context.chat_data["night_flow_review"]["favourite"] or ""
    proud: str = context.chat_data["night_flow_review"]["proud"] or ""
    improve: str = context.chat_data["night_flow_review"]["improve"] or ""
    comment: str = context.chat_data["night_flow_review"]["comment"] or ""

    # TODO: store review in database

    await send_message(
        update,
        context,
        "Recorded!",
    )

    await send_message(
        update,
        context,
        "Good job on takingthe time to reflect about your day!",
    )

    await send_message(
        update,
        context,
        "Now, let's plan your day for tomorrow...",
    )


@update_chat_data_state
async def night_flow_tomorrow_schedule(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_message(
        update,
        context,
        "Here's your schedule for tomorrow",
    )

    # TODO: get tomorrow schedule from calendar
    tomorrow_schedule = ""

    keyboard = [
        [
            InlineKeyboardButton(
                "Ok!", callback_data="night_flow_tomorrow_schedule_confirm"
            ),
        ],
        [
            InlineKeyboardButton(
                "Edit", callback_data="night_flow_tomorrow_schedule_edit"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        tomorrow_schedule,
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def night_flow_tomorrow_schedule_complete(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # TODO: get tomorrow schedule from calendar
    # TODO: update cron jobs

    await send_message(
        update,
        context,
        "You did a great job today!",
    )

    await send_message(
        update,
        context,
        "Time to rest!",
    )

    await send_message(
        update,
        context,
        "Good night!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def night_flow_tomorrow_schedule_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # TODO: direct to google calendar

    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="night_flow_tomorrow_schedule_edit_yes"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "Have you edited?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def night_flow_tomorrow_schedule_updated(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # TODO: sync gcal with database

    # TODO: get schedule from calendar
    tomorrow_schedule = ""

    # TODO: update cron jobs

    await send_message(
        update,
        context,
        "This is how your day tomorrow will look like then!\n\n" + tomorrow_schedule,
    )

    await send_message(
        update,
        context,
        "Goodnight!",
    )

    return ConversationHandler.END
