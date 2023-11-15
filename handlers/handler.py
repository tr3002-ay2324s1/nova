from telegram import Update
from telegram.ext import ContextTypes
from commands.event_command import (
    event_command_cancel,
    event_command_end,
    event_creation,
    event_date,
    event_end_time,
    event_start_time,
)
from commands.habit_command import (
    habit_command_end,
    habit_creation,
    habit_duration,
    habit_repetition,
    habit_schedule_edit,
    habit_schedule_updated,
)
from commands.task_command import (
    task_command_end,
    task_creation,
    task_deadline,
    task_duration,
    task_schedule_edit,
    task_schedule_updated,
)
from flows.block_flow import (
    block_created,
    block_end_alert_edit,
    block_flow_schedule_edit,
    block_next_alert,
    block_flow_schedule_updated,
    block_start_alert_confirm,
    block_update,
)
from flows.morning_flow import (
    morning_flow_end,
    morning_flow_schedule_edit,
    morning_flow_schedule_updated,
)
from flows.night_flow import (
    night_flow_comment,
    night_flow_favourite,
    night_flow_improve,
    night_flow_proud,
    night_flow_review_complete,
    night_flow_schedule,
    night_flow_tomorrow_schedule,
    night_flow_tomorrow_schedule_complete,
    night_flow_tomorrow_schedule_edit,
    night_flow_tomorrow_schedule_updated,
)

from utils.logger_config import configure_logger
from utils.unknown_response import unknown_command, unknown_text
from utils.utils import send_on_error_message

logger = configure_logger()


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        logger.error(
            "update.callback_query is None for handle_callback_query"
            + "\nupdate: "
            + str(update)
            + "\ncontext: "
            + str(context)
        )
        await send_on_error_message(context)
        return

    await query.answer()

    logger.info("handle_callback_query: " + str(query.data))

    if query.data == "":
        logger.error("query.data is empty for handle_callback_query")
        await send_on_error_message(context)
        return

    # event_command
    elif query.data == "event_creation_confirm":
        await event_command_end(
            update,
            context,
        )
    elif query.data == "event_creation_cancel":
        await event_command_cancel(update, context)

    # task_command
    elif query.data == "task_creation_confirm":
        await task_command_end(update, context)
    elif query.data == "task_creation_edit":
        await task_schedule_edit(update, context)
    elif query.data == "task_schedule_edit_yes":
        await task_schedule_updated(update, context)

    # habit_command
    elif query.data == "habit_creation_confirm":
        await habit_command_end(update, context)
    elif query.data == "habit_creation_edit":
        await habit_schedule_edit(update, context)
    elif query.data == "habit_schedule_edit_yes":
        await habit_schedule_updated(update, context)

    # morning flow
    elif query.data == "morning_flow_confirm":
        await morning_flow_end(update, context)
    elif query.data == "morning_flow_edit":
        await morning_flow_schedule_edit(update, context)
    elif query.data == "morning_flow_schedule_edit_yes":
        await morning_flow_schedule_updated(update, context)

    # block_flow
    elif query.data == "block_start_alert_confirm":
        await block_start_alert_confirm(update, context)
    elif query.data == "block_flow_schedule_edit":
        await block_flow_schedule_edit(update, context)
    elif query.data == "block_flow_schedule_edit_yes":
        await block_flow_schedule_updated(update, context)
    elif query.data == "block_end_alert_yes":
        await block_next_alert(update, context)
    elif query.data == "block_end_alert_no":
        await block_end_alert_edit(update, context)
    elif query.data == "block_update_yes":
        await block_created(update, context)
    elif query.data == "block_update_no":
        await block_flow_schedule_edit(update, context)

    # night_flow
    elif query.data == "night_flow_review_yes":
        await night_flow_schedule(update, context)
    elif query.data == "night_flow_review_skip":
        await night_flow_tomorrow_schedule(update, context)
    elif query.data == "night_flow_tomorrow_schedule_confirm":
        await night_flow_tomorrow_schedule_complete(update, context)
    elif query.data == "night_flow_tomorrow_schedule_edit":
        await night_flow_tomorrow_schedule_edit(update, context)
    elif query.data == "night_flow_tomorrow_schedule_edit_yes":
        await night_flow_tomorrow_schedule_updated(update, context)
    else:
        await unknown_command(update, context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for handle_text")
        await send_on_error_message(context)
        return
    if update.effective_message is None or update.effective_message.text is None:
        logger.error(
            "update.effective_message is None or update.effective_message.text is None for handle_text"
            + "\nupdate: "
            + str(update)
            + "\ncontext: "
            + str(context)
        )
        await send_on_error_message(context)
        return

    text = update.effective_message.text

    logger.info("handle_text: " + str(text))

    state = context.chat_data.get("state") if context.chat_data is not None else ""

    logger.info("state: " + str(state))

    if state == "":
        logger.error("state is empty for handle_text")
        await send_on_error_message(context)
        return

    # event_command
    elif state == "event_title":
        context.chat_data["new_event"]["title"] = text
        await event_date(update, context)
    elif state == "event_date":
        context.chat_data["new_event"]["date"] = text
        await event_start_time(update, context)
    elif state == "event_start_time":
        context.chat_data["new_event"]["start_time"] = text
        await event_end_time(update, context)
    elif state == "event_end_time":
        context.chat_data["new_event"]["end_time"] = text
        await event_creation(update, context)

    # task_command
    elif state == "task_title":
        context.chat_data["new_task"]["title"] = text
        await task_deadline(update, context)
    elif state == "task_deadline":
        context.chat_data["new_task"]["deadline"] = text
        await task_duration(update, context)
    elif state == "task_duration":
        context.chat_data["new_task"]["duration"] = text
        await task_creation(update, context)

    # habit_command
    elif state == "habit_title":
        context.chat_data["new_habit"]["title"] = text
        await habit_repetition(update, context)
    elif state == "habit_repetition":
        context.chat_data["new_habit"]["repetition"] = text
        await habit_duration(update, context)
    elif state == "habit_duration":
        context.chat_data["new_habit"]["duration"] = text
        await habit_creation(update, context)

    # block_flow
    elif state == "block_end_alert_edit":
        context.chat_data["block_update"]["duration"] = text
        await block_update(update, context)

    # night_flow
    elif state == "night_flow_feeling":
        context.chat_data["night_flow_review"]["feeling"] = text
        await night_flow_favourite(update, context)
    elif state == "night_flow_favourite":
        context.chat_data["night_flow_review"]["favourite"] = text
        await night_flow_proud(update, context)
    elif state == "night_flow_proud":
        context.chat_data["night_flow_review"]["proud"] = text
        await night_flow_improve(update, context)
    elif state == "night_flow_improve":
        context.chat_data["night_flow_review"]["improve"] = text
        await night_flow_comment(update, context)
    elif state == "night_flow_comment":
        context.chat_data["night_flow_review"]["comment"] = text
        await night_flow_review_complete(update, context)

    else:
        await unknown_text(update, context)
