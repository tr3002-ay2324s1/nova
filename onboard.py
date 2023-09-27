from telegram import Update
from telegram.ext import ContextTypes

from logger_config import configure_logger

logger = configure_logger()


async def onboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = ["Meditating", "Running"]
    message = await context.bot.send_poll(
        update.effective_chat.id,
        "What habit would you like to pick up?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)
