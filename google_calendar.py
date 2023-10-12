from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import fetch_user

from logger_config import configure_logger

logger = configure_logger()

async def google_login(
    update: Update, context: ContextTypes.DEFAULT_TYPE, auth_url: str, state: str
):
    if not update.callback_query or not update.callback_query.message or not context.chat_data:
        print("google_login: update.message or context.chat_data is None")
        return
    context.chat_data["state"] = "google_login"

    keyboard = [
        [
            InlineKeyboardButton("Login", url=auth_url),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(
        "Let's get started by setting up your Google Calendar 📅",
        reply_markup=reply_markup,
    )


async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "login_start"
    telegram_user_id = update.message.from_user.id

    user: List[dict] = fetch_user(telegram_user_id=telegram_user_id)

    if user and len(user) > 0:
      logger.info("USER: " + str(user))
      await update.message.reply_text(
          f"Nice to see you back {user[0].get('username', 'user')}"
      )
    else:
      keyboard = [
          [
              InlineKeyboardButton("Yes", callback_data="login_complete_yes"),
          ],
          [
              InlineKeyboardButton("No", callback_data="login_complete_no"),
          ],
      ]
      reply_markup = InlineKeyboardMarkup(keyboard)

      await update.message.reply_text(
          "Have you given permission for Google Cal before?", reply_markup=reply_markup
      )
