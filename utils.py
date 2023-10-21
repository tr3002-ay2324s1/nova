from functools import wraps
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


def update_chat_data_state(func):
    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        if context.chat_data is None:
            logger.error(f"context.chat_data is None for {func.__name__}")
            await send_on_error_message(context)
            return
        context.chat_data["state"] = func.__name__

        return await func(update, context, *args, **kwargs)

    return wrapper


def update_chat_data_state_context(func):
    @wraps(func)
    async def wrapper(context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if context.chat_data is None:
            logger.error(f"context.chat_data is None for {func.__name__}")
            await send_on_error_message(context)
            return
        context.chat_data["state"] = func.__name__

        return await func(context, *args, **kwargs)

    return wrapper


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


async def send_on_error_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(
        update=None,
        context=context,
        text="Something went wrong. Please try again later or contact @juliussneezer04 for help!",
    )
