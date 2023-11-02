from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from utils.logger_config import configure_logger
from utils.utils import (
    send_message,
    update_chat_data_state,
    update_chat_data_state_context,
)

logger = configure_logger()


@update_chat_data_state_context
async def morning_flow(context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(None, context, "Good morning! Here's how your day looks like:")

    # TODO: get schedule from calendar

    # TODO: generate updated schedule string
    schedule = "<schedule>"

    keyboard = [
        [
            InlineKeyboardButton("Ok!", callback_data="morning_flow_confirm"),
        ],
        [
            InlineKeyboardButton("Edit", callback_data="morning_flow_edit"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(None, context, schedule, reply_markup=reply_markup)


@update_chat_data_state
async def morning_flow_schedule_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
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
async def morning_flow_schedule_updated(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # TODO: sync gcal with database

    # TODO: update cron jobs

    await send_message(
        update,
        context,
        "Great!",
    )

    return ConversationHandler.END


@update_chat_data_state
async def morning_flow_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(None, context, "Great!")

    return ConversationHandler.END
