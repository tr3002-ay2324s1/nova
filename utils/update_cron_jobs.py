from datetime import datetime
from telegram.ext import ContextTypes
from flows.block_flow import block_start_alert
from flows.morning_flow import morning_flow
from lib.api_handler import get_user
from lib.google_cal import get_calendar_events
from utils.constants import DAY_START_TIME
from utils.job_queue import add_daily_job, add_once_job
from utils.logger_config import configure_logger
from utils.utils import send_on_error_message

logger = configure_logger()


async def update_cron_jobs(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for update_cron_jobs")
        await send_on_error_message(context)
        return

    # clear cron jobs
    if context.job_queue is None:
        logger.error("context.job_queue is None for update_cron_jobs")
        await send_on_error_message(context)
        return

    for job in context.job_queue.jobs():
        job.schedule_removal()
        logger.info(f"Job {job} removed")

    # add back morning flow
    await add_daily_job(
        callback=morning_flow,
        time=DAY_START_TIME,
        chat_id=context.chat_data["chat_id"],
        context=context,
    )

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
