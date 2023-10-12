from telegram import (
    Update,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
)
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def send_message(
    update: Update | None,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup: InlineKeyboardMarkup
    | ReplyKeyboardMarkup
    | ReplyKeyboardRemove
    | ForceReply
    | None = None,
):
    if update is not None and update.message is not None:
        await update.message.reply_text(text, reply_markup=reply_markup)
        return

    if update is not None and update.effective_message is not None:
        await update.effective_message.reply_text(text, reply_markup=reply_markup)
        return

    if (
        update is not None
        and update.callback_query is not None
        and update.callback_query.message is not None
    ):
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        return

    if context.job is not None and context.job.chat_id is not None:
        await context.bot.send_message(
            context.job.chat_id,
            text=text,
            reply_markup=reply_markup,
        )
        return
