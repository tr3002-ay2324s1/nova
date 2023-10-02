from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def morning_flow_greeting(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "morning_flow_greeting"

    await context.bot.send_message(
        context.job.chat_id, text=f"Good morning! Here's how your day looks like:"
    )

    await morning_flow_events(context)


async def morning_flow_events(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "morning_flow_events"

    # TODO: fetch data from database
    data = "<data from database>"

    # TODO: set up job queues here
    # for job in jobs:
    #     await add_daily_job(job, time, days, chat_id, context)

    keyboard = [
        [
            InlineKeyboardButton(
                "Looks Good!", callback_data="morning_flow_events_acknowledge"
            ),
        ],
        [
            InlineKeyboardButton("Edit", callback_data="morning_flow_events_edit"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        context.job.chat_id,
        text=str(data),
        reply_markup=reply_markup,
    )


async def morning_flow_events_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "morning_flow_events_edit"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="morning_flow_events_edit_yes"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Have you edited?",
        reply_markup=reply_markup,
    )


async def morning_flow_event(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "morning_flow_event"

    keyboard = [
        [
            InlineKeyboardButton("Ok!", callback_data="morning_flow_event_acknowledge"),
        ],
        [
            InlineKeyboardButton(
                "Change of Plans", callback_data="morning_flow_event_edit"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        context.job.chat_id,
        text="It's almost <time>. Time to work on the <task>!",
        reply_markup=reply_markup,
    )


async def morning_flow_event_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "morning_flow_event_edit"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="morning_flow_event_edit_yes"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Have you edited?",
        reply_markup=reply_markup,
    )


async def morning_flow_event_update(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "morning_flow_event_update"

    await update.message.reply_text("Updated your schedule!")

    # TODO: check database for next task
    # if next task exists:
    await update.message.reply_text("Nice job! Next up you have <task> at <time>!")


async def morning_flow_event_end(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "morning_flow_event_end"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="morning_flow_event_end_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="morning_flow_event_end_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        context.job.chat_id,
        text="How was your deep work session? Did you get it done?",
        reply_markup=reply_markup,
    )


async def morning_flow_next_event(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "morning_flow_next_event"

    # TODO: check database for next task
    # if next task exists:
    await update.message.reply_text("Nice job! Next up you have <task> at <time>!")


async def morning_flow_new_task(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "morning_flow_new_task"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="morning_flow_new_task_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="morning_flow_new_task_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "You have some time at <time>. Would you like to work on it then?",
        reply_markup=reply_markup,
    )
