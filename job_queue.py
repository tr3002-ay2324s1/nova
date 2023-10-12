from datetime import time
from telegram import Update
from telegram.ext import ContextTypes
import pytz

from logger_config import configure_logger

logger = configure_logger()


def remove_job_if_exists(job_name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with the given chat_id and job_name. Returns whether the job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
        logger.info(f"Job {job} removed, Name: {job_name}")
    return True


async def add_once_job(
    job, due: float, chat_id: int, context: ContextTypes.DEFAULT_TYPE
):
    """Add a once job to the queue."""
    if due < 0:
        await context.bot.send_message(
            chat_id=chat_id, text="Sorry we cannot go back to future!"
        )
        return

    job_name = f"{chat_id}_{job.__name__}_once"
    remove_job_if_exists(job_name, context)
    context.job_queue.run_once(job, due, chat_id=chat_id, name=job_name, data=due)

    logger.info(
        f"Once job added for chat ID {chat_id}. Due: {due}, Data: {due}, Name: {job_name}"
    )


async def add_daily_job(
    job,
    time: time,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Add a daily job to the queue."""
    job_name = f"{chat_id}_{job.__name__}_daily"
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

    data_string = str(time.isoformat()) + " " + str(days)

    context.job_queue.run_daily(
        job, time, days, chat_id=chat_id, name=job_name, data=data_string
    )

    logger.info(
        f"Daily job added for chat ID {chat_id}. Time: {time}, Days: {days}, Data: {data_string}, Name: {job_name}"
    )
