from telegram import Update
from telegram.ext import ContextTypes

from utils.logger_config import configure_logger

logger = configure_logger()


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        logger.info(
            "handle_callback_query: None"
            + "\nupdate: "
            + str(update)
            + "\ncontext: "
            + str(context)
        )
        return

    await query.answer()

    logger.info("handle_callback_query: " + str(query.data))

    # first_time
    if query.data == "google_login":
        await google_login(update, context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message is None or update.effective_message.text is None:
        logger.info("handle_text: None " + str(update))
        return

    text = update.effective_message.text

    logger.info("handle_text: " + str(text))

    chat_data = context.chat_data
    state = chat_data.get("state") if chat_data is not None else ""

    logger.info("state: " + str(state))

    if state == "add_task":
        await add_task(update, context, text)
