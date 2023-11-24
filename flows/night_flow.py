from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from lib.api_handler import get_user, plan_tasks
from lib.google_cal import (
    get_calendar_events,
    get_google_cal_link,
    get_readable_cal_event_str,
)
from utils.datetime_utils import (
    get_day_start_end_datetimes,
    get_tomorrow_start_end_datetimes,
)
from utils.logger_config import configure_logger
from utils.utils import (
    send_message,
    send_on_error_message,
    update_chat_data_state,
)

logger = configure_logger()


@update_chat_data_state
async def night_flow_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="night_flow_review_yes"),
        ],
        [
            InlineKeyboardButton("Skip", callback_data="night_flow_review_skip"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        "That's the end of your work day! Would you like to review now?",
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def night_flow_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    timeMin, timeMax = get_day_start_end_datetimes()
    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=timeMin.isoformat(),
        timeMax=timeMax.isoformat(),
        k=150,
    )
    schedule = get_readable_cal_event_str(events) or "No upcoming events found."

    await send_message(
        update,
        context,
        "Today you:\n" + schedule,
    )

    await night_flow_feeling(update, context)


@update_chat_data_state
async def night_flow_feeling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "How are you feeling?",
    )


@update_chat_data_state
async def night_flow_favourite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What was your favourite part of the day?",
    )


@update_chat_data_state
async def night_flow_proud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What are you proud of yourself for today?",
    )


@update_chat_data_state
async def night_flow_improve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "What was one thing you can improve on?",
    )


@update_chat_data_state
async def night_flow_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update,
        context,
        "Anything else you want to record for today?",
    )


@update_chat_data_state
async def night_flow_review_complete(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    feeling: str = context.chat_data["night_flow_review"]["feeling"] or ""
    favourite: str = context.chat_data["night_flow_review"]["favourite"] or ""
    proud: str = context.chat_data["night_flow_review"]["proud"] or ""
    improve: str = context.chat_data["night_flow_review"]["improve"] or ""
    comment: str = context.chat_data["night_flow_review"]["comment"] or ""

    # TODO: store review in database

    await send_message(
        update,
        context,
        "Recorded!",
    )

    await send_message(
        update,
        context,
        "Good job on takingthe time to reflect about your day!",
    )

    await send_message(
        update,
        context,
        "Now, let's plan your day for tomorrow...",
    )

    await night_flow_tomorrow_schedule(update, context)


@update_chat_data_state
async def night_flow_tomorrow_schedule(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    await send_message(
        update,
        context,
        "Here's your schedule for tomorrow!",
    )

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    timeMin, timeMax = get_tomorrow_start_end_datetimes()
    tomorrow_events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=timeMin.isoformat(),
        timeMax=timeMax.isoformat(),
        k=150,
    )
    tomorrow_schedule = (
        get_readable_cal_event_str(tomorrow_events) or "No upcoming events found."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "Ok!", callback_data="night_flow_tomorrow_schedule_confirm"
            ),
        ],
        [
            InlineKeyboardButton(
                "Edit",
                callback_data="night_flow_tomorrow_schedule_edit",
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update,
        context,
        tomorrow_schedule,
        reply_markup=reply_markup,
    )


@update_chat_data_state
async def night_flow_tomorrow_schedule_complete(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_message(
        update,
        context,
        "You did a great job today!",
    )

    await send_message(
        update,
        context,
        "Time to rest!",
    )

    await night_flow_end(update, context)


@update_chat_data_state
async def night_flow_tomorrow_schedule_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    url = get_google_cal_link(user_id)

    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="night_flow_tomorrow_schedule_edit_yes"
            ),
        ],
        [
            InlineKeyboardButton(
                "Click me to go to Google Calendar",
                url=url,
            ),
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
async def night_flow_tomorrow_schedule_updated(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)
    timeMin, timeMax = get_tomorrow_start_end_datetimes()
    tomorrow_events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        timeMin=timeMin.isoformat(),
        timeMax=timeMax.isoformat(),
        k=150,
    )
    tomorrow_schedule = (
        get_readable_cal_event_str(tomorrow_events) or "No upcoming events found."
    )

    await send_message(
        update,
        context,
        "This is how your day tomorrow will look like then!\n\n" + tomorrow_schedule,
    )

    await night_flow_end(update, context)


@update_chat_data_state
async def night_flow_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for event_creation")
        await send_on_error_message(context)
        return

    plan_tasks(context.chat_data["chat_id"])

    await send_message(
        update,
        context,
        "Good night!",
    )

    return ConversationHandler.END
