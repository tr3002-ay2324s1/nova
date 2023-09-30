from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()

from task import task_dateline, end_add_task


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.info("handle_callback_query: " + str(query.data))

    # first_time
    if query.data == "acknowledge":
        print("handle_callback_query")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text

    logger.info("handle_text: " + str(text))

    if "state" in context.chat_data.keys():
        state = context.chat_data["state"]
    else:
        state = ""

    logger.info("state: " + str(state))

    if state == "add_task":
        # TODO: generate task duration here
        await task_dateline(update, context)

    elif state == "task_dateline":
        # TODO: save task here
        await end_add_task(update, context)
