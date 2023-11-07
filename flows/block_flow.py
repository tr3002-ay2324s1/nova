from datetime import datetime
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from flows.night_flow import night_flow_review
from utils.job_queue import add_once_job
from utils.logger_config import configure_logger
from utils.utils import (
    send_message,
    send_on_error_message,
    update_chat_data_state,
    update_chat_data_state_context,
)

logger = configure_logger()


@update_chat_data_state_context
async def block_start_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.job is None:
        logger.error("context.job is None for block_alert")
        await send_on_error_message(context)
        return
    if context.job.name is None:
        logger.error("context.job.name is None for block_alert")
        await send_on_error_message(context)
        return

    keyboard = [
        [
            InlineKeyboardButton("Ok!", callback_data="block_start_alert_confirm"),
        ],
        [
            InlineKeyboardButton(
                "Change of Plans", callback_data="block_flow_schedule_edit"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    parts = context.job.name.split("_")
    time = parts[3]
    name = parts[6]

    await send_message(
        None,
        context,
        "It's almost " + time[:2] + ":" + time[-2:] + ". Time to work on " + name,
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def block_start_alert_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for block_start_alert_confirm")
        await send_on_error_message(context)
        return

    # TODO: get block end time

    await add_once_job(
        callback=block_end_alert,
        when=(datetime.now()),
        chat_id=context.chat_data["chat_id"],
        context=context,
        data="<task_name>",
    )

    return ConversationHandler.END


@update_chat_data_state
async def block_flow_schedule_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: direct to google calendar

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="block_flow_schedule_edit_yes"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "Have you edited?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def block_flow_schedule_updated(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # TODO: sync gcal with database

    # TODO: get schedule from calendar
    schedule = ""

    # TODO: update cron jobs

    await send_message(
        update,
        context,
        "Updated your schedule!\n\n" + schedule,
    )

    await block_next_alert(update, context)


@update_chat_data_state
async def block_next_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: get schedule from calendar
    schedule = ""

    # TODO: check if there is any upcoming block for the day
    has_upcoming_block = False

    if has_upcoming_block:
        task = ""
        time = ""
        await send_message(
            update,
            context,
            "Nice job! Next up you have " + task + " at " + time,
        )
    else:
        await night_flow_review(update, context)


@update_chat_data_state_context
async def block_end_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="block_end_alert_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="block_end_alert_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        None,
        context,
        "Time's up! Did you get it done?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def block_end_alert_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "How much more time do you need? (in minutes)",
    )


@update_chat_data_state
async def block_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for block_update")
        await send_on_error_message(context)
        return

    duration = context.chat_data["block_update"]["duration"]
    # TODO: checks for the first free slot
    time = ""

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="block_update_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="block_update_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "You have some time at " + time + ". Would you like to work on it then?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def block_created(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: create new event on gcal

    await block_flow_schedule_updated(update, context)
