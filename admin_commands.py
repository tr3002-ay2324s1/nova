from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from logger_config import configure_logger

logger = configure_logger()

from job_queue import add_once_job
from morning_flow import morning_flow_greeting


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "start_command"

    logger.info("user_id: " + str(update.message.from_user.id))
    logger.info("tele_handle: " + str(update.message.from_user.username))

    await add_once_job(
        morning_flow_greeting, 2, update.effective_message.chat_id, context
    )

    await update.message.reply_text(
        """
                                    hey there :) welcome to brio,
your personal habit tracker 💪🏽
"""
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "help_command"

    await update.message.reply_text(
        """
        Available Commands:
        /start - Start Study Buddy Telegram Bot
        """
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.chat_data["state"] = "cancel_command"

    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
