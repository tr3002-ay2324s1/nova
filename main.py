from telegram.ext import Application, CommandHandler, MessageHandler, filters

import os
from dotenv import load_dotenv

from error_handlers import error_handler
from admin_commands import start_command, help_command
from unknown import unknown_command, unknown_text

load_dotenv()


if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN") or ""
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Unknown
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(filters.TEXT, unknown_text))

    # Errors
    app.add_error_handler(error_handler)

    # Polls the bot
    app.run_polling(poll_interval=3)
