from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import os
import html
import json
import traceback
from lib.api_handler import get_google_oauth_login_url
from utils.logger_config import configure_logger
from utils.utils import send_message

logger = configure_logger()


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    if context.error is not None:
        if len(context.error.args) > 1 and "error" in context.error.args[1] and context.error.args[1]["error"] == "invalid_grant":
            user_id = context.chat_data.get("chat_id", "") if context.chat_data else ""
            username = (update.message and update.message.from_user and update.message.from_user.username) or "user"
            url = get_google_oauth_login_url(
                telegram_user_id=user_id,
                username=username,
            )

            await send_message(
                update,
                context,
                "You'll need to login to Google Calendar again!",
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "Click me!", url=url
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await send_message(
                update,
                context,
                "Login to Google Calendar to get started!",
                reply_markup=reply_markup,
            )
            return
            
        tb_list: list[str] = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        tb_string = "".join(tb_list)
    else:
        tb_string = "No traceback available"

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID") or ""

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )
