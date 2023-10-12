from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from logger_config import configure_logger

logger = configure_logger()

from utils import send_message
from google_calendar import login_start
from job_queue import add_daily_job
from morning_flow import morning_flow_greeting
from datetime import time


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "start_command"
        logger.info("state: " + context.chat_data["state"])

    if update.message is not None and update.message.from_user is not None:
        logger.info("user_id: " + str(update.message.from_user.id))
        logger.info("tele_handle: " + str(update.message.from_user.username))

    if update.message is not None:
        await add_daily_job(
            morning_flow_greeting, time(8, 0), update.message.chat_id, context
        )

    await send_message(
        update,
        context,
        """
    hey there :)
welcome to nova,
your personal assistant 💪🏽
    """,
    )

    await login_start(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "help_command"

    await send_message(
        update,
        context,
        """
        Available Commands:
        /start - Start Study Buddy Telegram Bot
        """,
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.chat_data is not None:
        context.chat_data["state"] = "cancel_command"

    if update.message is not None and update.message.from_user is not None:
        logger.info(
            "User %s canceled the conversation.", update.message.from_user.first_name
        )

    await send_message(
        update,
        context,
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END
