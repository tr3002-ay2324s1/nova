from telegram import Update
from telegram.ext import ContextTypes

from onboard import onboard

from logger_config import configure_logger

logger = configure_logger()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("user_id: " + str(update.message.from_user.id))
    logger.info("tele_handle: " + str(update.message.from_user.username))

    await update.message.reply_text(
        """
                                    hey there :) welcome to brio,
your personal habit tracker 💪🏽

type /onboard to get started!
"""
    )

    await onboard(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
        Available Commands:
        /start - Start Study Buddy Telegram Bot
        """
    )
