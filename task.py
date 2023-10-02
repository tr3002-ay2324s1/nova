from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "add_task"

    await update.message.reply_text("What is the name of the task?")


async def task_dateline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "task_dateline"

    await update.message.reply_text(
        "When would you like to complete this task by? (answer in MDYY format)"
    )


async def end_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "end_add_task"

    await update.message.reply_text("Task saved!")
