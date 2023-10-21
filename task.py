from telegram import Update
from telegram.ext import ContextTypes
from utils import send_message, update_chat_data_state
from logger_config import configure_logger

logger = configure_logger()


@update_chat_data_state
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, context, "What is the name of the task?")


@update_chat_data_state
async def end_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, context, "Task added!")
