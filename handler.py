from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from logger_config import configure_logger

logger = configure_logger()

from task import task_dateline, end_add_task
from morning_flow import (
    morning_flow_event_edit,
    morning_flow_event_update,
    morning_flow_next_event,
    morning_flow_new_task,
)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.info("handle_callback_query: " + str(query.data))

    # first_time
    if query.data == "morning_flow_events_acknowledge":
        # TODO: save morning_flow_events_acknowledge here
        return ConversationHandler.END
    elif query.data == "morning_flow_events_edit":
        # TODO: sync google calendar here
        # TODO: update daily job here
        return ConversationHandler.END
    elif query.data == "morning_flow_event_acknowledge":
        # TODO: add daily job here
        return ConversationHandler.END
    elif query.data == "morning_flow_event_edit":
        # TODO: direct to google calendar here
        await morning_flow_event_edit(update, context)
    elif query.data == "morning_flow_event_edit_yes":
        # TODO: sync google calendar here
        # TODO: update daily job here
        await morning_flow_event_update(update, context)
    elif query.data == "morning_flow_event_end_yes":
        await morning_flow_next_event(update, context)
    elif query.data == "morning_flow_event_end_no":
        # TODO: generate next potential task timing here
        await morning_flow_new_task(update, context)
    elif query.data == "morning_flow_new_task_yes":
        # TODO: update new task in google calendar
        # TODO: update daily job here
        await morning_flow_event_update(update, context)
    elif query.data == "morning_flow_new_task_no":
        # TODO: direct to googl ecalendar here
        await morning_flow_event_edit(update, context)


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
