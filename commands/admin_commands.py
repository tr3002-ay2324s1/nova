from datetime import datetime, time, timedelta
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler
from flows.block_flow import block_start_alert
from flows.morning_flow import morning_flow
from utils.constants import DAY_START_TIME
from utils.job_queue import add_daily_job, add_once_job
from utils.logger_config import configure_logger
from utils.utils import send_message, send_on_error_message, update_chat_data_state

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
    # note that chat_id and user_id are the same for private chat
    context.chat_data["chat_id"] = int(update.message.chat_id)

    # add morning flow job
    await add_daily_job(
        callback=morning_flow,
        time=DAY_START_TIME,
        chat_id=context.chat_data["chat_id"],
        context=context,
    )

    await add_once_job(
        callback=block_start_alert,
        when=(datetime.now() + timedelta(minutes=4)),
        chat_id=context.chat_data["chat_id"],
        context=context,
        data="<task_name>",
    )

    await send_message(
        update,
        context,
        "hey there :)\nI am nova,\nyour personal assistant 💪🏽",
    )


@update_chat_data_state
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Available Commands:\n/start - Activate Nova\n/events - Show my schedule for the day\n/add - Add a task to be done\n/tasks - Show all my added tasks\n/cancel - Cancel the current command\n/help - Show this message",
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
