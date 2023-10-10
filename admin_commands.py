from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from logger_config import configure_logger

logger = configure_logger()

from job_queue import add_once_job
from morning_flow import morning_flow_greeting
import google_auth_oauthlib.flow

async def get_login_google():
  # Use the credentials.json file to identify the application requesting
  # authorization. The client ID (from that file) and access scopes are required.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      'credentials.json',
      scopes=['https://www.googleapis.com/auth/calendar.events'])

  # Indicate where the API server will redirect the user after the user completes
  # the authorization flow. The redirect URI is required. The value must exactly
  # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
  # configured in the API Console. If this value doesn't match an authorized URI,
  # you will get a 'redirect_uri_mismatch' error.
  flow.redirect_uri = 'http://127.0.0.1:8000/google_oauth_callback'

  # Generate URL for request to Google's OAuth 2.0 server.
  # Use kwargs to set optional request parameters.
  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')
  
  authorization_url: str
  state: str

  return authorization_url, state


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.chat_data["state"] = "start_command"

  if update.message is None or update.message.from_user is None:
    return
  logger.info("user_id: " + str(update.message.from_user.id))
  logger.info("tele_handle: " + str(update.message.from_user.username))

  if update.effective_message is not None:
    chat_id = update.effective_message.chat_id
    await add_once_job(morning_flow_greeting, 2, chat_id, context)

  await update.message.reply_text(
    """
    hey there :)
welcome to nova,
your personal assistant 💪🏽
    """
  )

  url, state = await get_login_google()

  await update.message.reply_text("First off, we'll need your google calendar access")

  await update.message.reply_text(parse_mode="HTML", text=f"Please login to your google account here by going to <a href='{url}'>this link</a>")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["state"] = "help_command"

    await update.message.reply_text(
        """
        Available Commands:
        /start - Start Study Buddy Telegram Bot
        """
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.chat_data["state"] = "cancel_command"

    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
