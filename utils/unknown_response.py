from random import randint
from telegram import Update
from telegram.ext import ContextTypes
from utils.constants import READYMADE_RESPONSES
from utils.logger_config import configure_logger
from utils.utils import send_message, update_chat_data_state

logger = configure_logger()


@update_chat_data_state
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is not None and update.message.text is not None:
        await send_message(
            update,
            context,
            update.message.text
            + " is not a valid command. Please use /start to start again.",
        )


@update_chat_data_state
async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is not None and update.message.text is not None:
        await send_message(
            update,
            context,
            "Sorry, I don't understand that. Please use /start to start again.",
        )
        # # Pick quote from array READYMADE_RESPONSES
        # rand_idx = randint(0, len(READYMADE_RESPONSES) - 1)
        # quote = READYMADE_RESPONSES[rand_idx]
        # await send_message(
        #     update,
        #     context,
        #     "Hey! " + quote,
        # )
