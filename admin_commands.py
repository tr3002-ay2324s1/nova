from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler
from constants import MORNING_FLOW_TIME
from logger_config import configure_logger
from utils import send_message, send_on_error_message, update_chat_data_state
from google_oauth_utils import login_start
from job_queue import add_daily_job
from morning_flow import morning_flow_greeting
from datetime import time

logger = configure_logger()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for start_command")
        context.chat_data = dict()
    if update.message is None:
        logger.error("update.message is None for start_command")
        await send_on_error_message(context)
        return
    if update.message.from_user is None:
        logger.error("update.message.from_user is None for start_command")
        await send_on_error_message(context)
        return

    context.chat_data["state"] = "start_command"
    context.chat_data["user_id"] = str(update.message.from_user.id)
    context.chat_data["chat_id"] = str(update.message.chat_id)
    logger.info("user_id: " + str(update.message.from_user.id))
    logger.info("tele_handle: " + str(update.message.from_user.username))

    await add_daily_job(
        morning_flow_greeting,
        time(MORNING_FLOW_TIME[0], MORNING_FLOW_TIME[1]),
        update.message.chat_id,
        context,
    )

    await send_message(
        update,
        context,
        """
    hey there :)
I am nova,
your personal assistant 💪🏽
    """,
    )

    await login_start(update, context)


@update_chat_data_state
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        """
        Available Commands:
/start - Activate Nova
/events - Show my schedule for the day
/add - Add a task to be done
/tasks - Show all my added tasks
/cancel - Cancel the current command
/help - Show this message
        """,
    )


@update_chat_data_state
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_message(
        update,
        context,
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END
