from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from logger_config import configure_logger

logger = configure_logger()

from datetime import datetime, timedelta

from task import task_dateline, end_add_task
from job_queue import add_once_job
from google_calendar import login_complete
from morning_flow import (
    morning_flow_event_edit,
    morning_flow_event_update,
    morning_flow_next_event,
    morning_flow_new_task,
)
from night_flow import (
    night_flow_review,
    night_flow_feeling,
    night_flow_favourite,
    night_flow_proud,
    night_flow_improve,
    night_flow_next_day_schedule,
    night_flow_pick_time,
    night_flow_invalid_time,
    night_flow_skip,
    night_flow_end,
    night_flow_next_day_schedule_edit,
)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.info("handle_callback_query: " + str(query.data))

    # first_time
    if query.data == "google_login":
        # TODO: login to google calendar
        await login_complete(update, context)
    elif query.data == "login_complete_yes":
        # TODO: update database that login complete
        return ConversationHandler.END
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
        # TODO: direct to google ecalendar here
        await morning_flow_event_edit(update, context)
    elif (
        query.data == "night_flow_review_yes"
        or query.data == "night_flow_new_review_time_yes"
    ):
        # TODO: update database with events completed if needed
        await night_flow_feeling(update, context)
    elif query.data == "night_flow_review_no":
        await night_flow_pick_time(update, context)
    elif query.data == "night_flow_new_review_time_skip":
        await night_flow_skip(update, context)
    elif query.data == "night_flow_next_day_schedule_ok":
        await night_flow_end(update, context)
    elif query.data == "night_flow_next_day_schedule_edit":
        # TODO: direct to google calendar here
        await night_flow_next_day_schedule_edit(update, context)
    elif query.data == "night_flow_next_day_schedule_edit_yes":
        # TODO: sync google calendar here
        # TODO: fetch next day data from database
        await night_flow_next_day_schedule(update, context)


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
    elif state == "night_flow_feeling":
        # TODO: save night_flow_feeling here
        await night_flow_favourite(update, context)
    elif state == "night_flow_favourite":
        # TODO: save night_flow_favourite here
        await night_flow_proud(update, context)
    elif state == "night_flow_proud":
        # TODO: save night_flow_proud here
        await night_flow_improve(update, context)
    elif state == "night_flow_improve":
        # TODO: fetch next day data from database
        await night_flow_next_day_schedule(update, context)
    elif state == "night_flow_pick_time":
        return await validate_night_flow_pick_time(update, context, text)
    elif state == "night_flow_invalid_time":
        return await validate_night_flow_pick_time(update, context, text)


async def validate_night_flow_pick_time(update, context, text):
    if text == None:
        await night_flow_invalid_time(update, context)
    else:
        try:
            # Parse the input to a datetime object.
            input_time = datetime.strptime(text, "%H%M").time()

            # Get current datetime and time.
            current_datetime = datetime.now()
            current_time = current_datetime.time()

            # Create datetime objects for comparison.
            current_dt = datetime.combine(current_datetime.date(), current_time)
            input_dt = datetime.combine(current_datetime.date(), input_time)

            # Check if input time is earlier than the current time.
            # If yes, assume it's for the next day.
            if input_dt <= current_dt:
                input_dt += timedelta(days=1)

                # Calculate the number of seconds from now till the input time.
            delta_seconds = (input_dt - current_dt).seconds

            await add_once_job(
                night_flow_review, delta_seconds, update.effective_chat.id, context
            )

            return ConversationHandler.END
        except ValueError:
            # Invalid time format; invoke the night_flow_invalid_time function.
            await night_flow_invalid_time(update, context)
