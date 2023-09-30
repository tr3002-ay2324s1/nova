from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def greeting(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        context.job.chat_id, text=f"Good morning! Here's how your day looks like:"
    )
