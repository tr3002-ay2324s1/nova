from dotenv import load_dotenv
from os import environ
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
from admin import start, help, unknown_command, unknown_text

load_dotenv()

EXPECT_TEXT = range(1)


if __name__ == "__main__":
    api_key = environ.get("API_KEY")
    application = ApplicationBuilder().token(api_key).build()

    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
    unknown_text_handler = MessageHandler(filters.TEXT, unknown_text)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(unknown_command_handler)
    application.add_handler(unknown_text_handler)

    application.run_polling()
