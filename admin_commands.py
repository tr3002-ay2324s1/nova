from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from logger_config import configure_logger

logger = configure_logger()

from google_calendar import google_login


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "start_command"

    logger.info("user_id: " + str(update.message.from_user.id))
    logger.info("tele_handle: " + str(update.message.from_user.username))

    await update.message.reply_text(
        "Hey there :)\nWelcome to Nova, your personal habit tracker 💪🏽"
    )

    await google_login(update, context)


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
