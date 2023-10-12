from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from logger_config import configure_logger

logger = configure_logger()


async def night_flow_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "night_flow_review"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="night_flow_review_yes"),
        ],
        [
            InlineKeyboardButton("No", callback_data="night_flow_review_no"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "That's the end of your work day! Would you like to review now?",
        reply_markup=reply_markup,
    )


async def night_flow_feeling(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "night_flow_feeling"

    # TODO: fetch data from database

    await update.message.reply_text(
        "Today you completed tasks <a>, <b>, <c>. How are you feeling?"
    )


async def night_flow_favourite(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "night_flow_favourite"

    await update.message.reply_text("What was your favourite part of the day?")


async def night_flow_proud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "night_flow_proud"

    await update.message.reply_text("What are you proud of yourself for today?")


async def night_flow_improve(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "night_flow_improve"

    await update.message.reply_text("What was one thing you can improve on?")


async def night_flow_next_day_schedule(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "night_flow_next_day_schedule"

    keyboard = [
        [
            InlineKeyboardButton(
                "Ok!", callback_data="night_flow_next_day_schedule_ok"
            ),
        ],
        [
            InlineKeyboardButton(
                "Edit", callback_data="night_flow_next_day_schedule_edit"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Here's your schedule for tomorrow!")

    # TODO: fetch data from database

    await update.message.reply_text("<schedule>", reply_markup=reply_markup)


async def night_flow_pick_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "night_flow_pick_time"

    await update.message.reply_text(
        "Pick a time to review later (answer in 24h format e.g. 1800 for 6pm)"
    )


async def night_flow_invalid_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "night_flow_invalid_time"

    await update.message.reply_text(
        "Invalid Time! Please try again. (answer in 24h format e.g. 1800 for 6pm)"
    )


async def night_flow_new_review_time(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "night_flow_new_review_time"

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="night_flow_new_review_time_yes"),
        ],
        [
            InlineKeyboardButton(
                "Skip", callback_data="night_flow_new_review_time_skip"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        context.job.chat_id,
        text="It is time to review your day!",
        reply_markup=reply_markup,
    )


async def night_flow_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["state"] = "night_flow_skip"

    await update.message.reply_text(
        "Alright, let's get straight to planning for tomorrow then!"
    )

    await night_flow_next_day_schedule(update, context)


async def night_flow_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "night_flow_end"

    await update.message.reply_text("Good night!")

    return ConversationHandler.END


async def night_flow_next_day_schedule_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.chat_data["state"] = "night_flow_next_day_schedule_edit"

    keyboard = [
        [
            InlineKeyboardButton(
                "Yes", callback_data="night_flow_next_day_schedule_edit_yes"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Have you edited?",
        reply_markup=reply_markup,
    )
