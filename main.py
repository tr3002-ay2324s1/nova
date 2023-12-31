from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
)
import os
from dotenv import load_dotenv
from commands.admin_commands import cancel_command, help_command, refresh_command, schedule_command, start_command
from commands.event_command import event_title
from commands.habit_command import habit_title
from commands.task_command import task_title
from handlers.error_handlers import error_handler
from handlers.handler import handle_callback_query, handle_text
from utils.unknown_response import unknown_command, unknown_text
from enum import Enum

load_dotenv()

EXPECT_TEXT = range(1)


# make command Enum
class Command(str, Enum):
    START = "start"
    HELP = "help"
    CANCEL = "cancel"
    EVENT = "event"
    TASK = "task"
    HABIT = "habit"
    SCHEDULE = "schedule"
    REFRESH = "refresh"


if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN") or ""
    # TOKEN = os.getenv("STAGING_TOKEN") or ""
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler(Command.START, start_command))
    app.add_handler(CommandHandler(Command.HELP, help_command))
    app.add_handler(CommandHandler(Command.CANCEL, cancel_command))

    app.add_handler(CommandHandler(Command.EVENT, event_title))
    app.add_handler(CommandHandler(Command.TASK, task_title))
    app.add_handler(CommandHandler(Command.HABIT, habit_title))

    app.add_handler(CommandHandler(Command.SCHEDULE, schedule_command))
    app.add_handler(CommandHandler(Command.REFRESH, refresh_command))

    # Handlers
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT, handle_text)],
        states={EXPECT_TEXT: [MessageHandler(filters.TEXT, handle_text)]},
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(conv_handler)

    # Unknown
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(filters.TEXT, unknown_text))

    # Errors
    app.add_error_handler(error_handler)

    # Polls the bot
    app.run_polling(poll_interval=3, allowed_updates=Update.ALL_TYPES)
