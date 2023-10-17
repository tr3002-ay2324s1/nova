from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()

from utils import send_message


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "add_task"

    await send_message(update, context, "What is the name of the task?")


# async def task_dateline(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if context.chat_data is not None:
#         context.chat_data["state"] = "task_dateline"

#     await send_message(
#         update,
#         context,
#         "When would you like to complete this task by? (answer in MDYY format e.g. 1121 for 1 Jan 2021 and 111122 for 11 Nov 2022)",
#     )


async def end_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is not None:
        context.chat_data["state"] = "end_add_task"

    await send_message(update, context, "Task added!")
