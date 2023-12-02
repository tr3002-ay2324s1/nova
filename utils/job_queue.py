from datetime import datetime, time, timedelta
from typing import Optional
from telegram.ext import ContextTypes
from utils.constants import NEW_YORK_TIMEZONE_INFO

from utils.logger_config import configure_logger
from utils.utils import send_on_error_message

logger = configure_logger()


def remove_job_if_exists(job_name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with the given chat_id and job_name. Returns whether the job was removed."""
    if context.job_queue is None:
        return False
    current_jobs = (
        context.job_queue.get_jobs_by_name(job_name) if context.job_queue else []
    )

    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
        logger.info(f"Job {job} removed, Name: {job_name}")
    return True


async def add_once_job(
    callback,
    when: datetime,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    data: Optional[str] = None,
):
    """Add a once job to the queue."""
    when_formatted = when.strftime("%Y%m%d_%H%M")
    job_name_suffix = f"_{data}" if data else ""
    job_name = f"once_{callback.__name__}_{when_formatted}_{chat_id}{job_name_suffix}"

    remove_job_if_exists(job_name, context)

    # Explicitly set the time zone to America/New_York
    # Fix bug: Localize timezone to fix bug of timezone being %Z:56 instead of %Z:00
    # Fix bug: Add 20 seconds to when to fix bug of instantly added job not being run
    when = NEW_YORK_TIMEZONE_INFO.localize(when.replace(tzinfo=None)) + timedelta(seconds=20)

    if context.job_queue is not None:
        context.job_queue.run_once(
            callback, when, chat_id=chat_id, name=job_name, data=data
        )

        logger.info(f"Once job {job_name} added for {chat_id} at {when}")


async def add_daily_job(
    callback,
    time: time,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    data: Optional[str] = None,
):
    """Add a daily job to the queue."""
    time_formatted = time.strftime("%H%M")
    job_name_suffix = f"_{data}" if data else ""
    job_name = f"daily_{callback.__name__}_{time_formatted}_{chat_id}{job_name_suffix}"

    remove_job_if_exists(job_name, context)

    # Explicitly set the time zone to America/New_York
    time = time.replace(tzinfo=NEW_YORK_TIMEZONE_INFO)

    if context.job_queue is not None:
        daily_job = context.job_queue.run_daily(
            callback,
            time,
            days=tuple(range(7)),
            chat_id=chat_id,
            name=job_name,
            data=data,
        )

        logger.info(f"Daily job {job_name} added for {chat_id} at {time}")
        logger.info("Next run at " + str(daily_job.next_t))


async def clear_cron_jobs(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data is None:
        logger.error("context.chat_data is None for clear_cron_jobs")
        await send_on_error_message(context)
        return
    if context.job_queue is None:
        logger.error("context.job_queue is None for clear_cron_jobs")
        await send_on_error_message(context)
        return

    for job in context.job_queue.jobs():
        job.schedule_removal()
        logger.info(f"Job {job} removed")
