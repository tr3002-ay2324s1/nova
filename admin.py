from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("user_id: " + str(update.message.from_user.id))
    print("tele_handle: " + str(update.message.from_user.username))

    await update.message.reply_text("Hello, I'm a bot, please talk to me!")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
    Available Commands:
    /start - Start Study Buddy Telegram Bot
    """
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text + " is not a valid command. Please use /start to start again.")


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text + " is not a valid text. Please use /start to start again.")
