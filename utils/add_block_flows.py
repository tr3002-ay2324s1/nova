from datetime import datetime
from telegram.ext import ContextTypes
from utils.logger_config import configure_logger
from utils.utils import send_on_error_message

logger = configure_logger()


async def add_block_flows(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for add_morning_flow")
        await send_on_error_message(context)
        return

    from flows.block_flow import block_start_alert
    from lib.api_handler import get_user
    from lib.google_cal import get_calendar_events
    from utils.job_queue import add_once_job

    user_id = context.chat_data["chat_id"]
    user = get_user(user_id)

    events = get_calendar_events(
        refresh_token=user.get("google_refresh_token", ""),
        k=500,
    )

    for event in events:
        name = event.get("summary")

        # will not work for all day events, assume that start always has dateTime
        start_datetime_str = event.get("start").get("dateTime")

        if start_datetime_str is None:
            logger.error("start_datetime_str is None for event")
            await send_on_error_message(context)
            return

        start_datetime = datetime.fromisoformat(start_datetime_str)

        await add_once_job(
            callback=block_start_alert,
            when=start_datetime,
            chat_id=int(context.chat_data["chat_id"]),
            context=context,
            data=name,
        )
