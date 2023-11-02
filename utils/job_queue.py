from datetime import time
from telegram import Update
from telegram.ext import ContextTypes
import pytz

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
    callback, when: time, chat_id: int, context: ContextTypes.DEFAULT_TYPE
):
    """Add a once job to the queue."""
    job_name = f"{chat_id}_{callback.__name__}_once"
    remove_job_if_exists(job_name, context)

    # Explicitly set the time zone to America/New_York
    when = when.replace(tzinfo=pytz.timezone("America/New_York"))

    if context.job_queue is not None:
        context.job_queue.run_once(callback, when, chat_id=chat_id, name=job_name)

        logger.info(f"Once job {job_name} added for {chat_id} at {when}")


async def add_daily_job(
    callback,
    time: time,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Add a daily job to the queue."""
    job_name = f"{chat_id}_{callback.__name__}_daily"
    remove_job_if_exists(job_name, context)

    # Explicitly set the time zone to America/New_York
    time = time.replace(tzinfo=pytz.timezone("America/New_York"))

    days = (
        0,
        1,
        2,
        3,
        4,
        5,
        6,
    )  # The job will run every day (0=Monday, 1=Tuesday, ..., 6=Sunday)

    if context.job_queue is not None:
        context.job_queue.run_daily(
            callback, time, days, chat_id=chat_id, name=job_name
        )

        logger.info(f"Daily job {job_name} added for {chat_id} at {time} every {days}")


async def clear_cron_jobs(context: ContextTypes.DEFAULT_TYPE):
    if context.job_queue is None:
        logger.error("context.job_queue is None for clear_cron_jobs")
        await send_on_error_message(context)
        return

    for job in context.job_queue.jobs():
        job.schedule_removal()
        logger.info(f"Job {job} removed")
