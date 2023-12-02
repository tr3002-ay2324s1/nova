from telegram.ext import ContextTypes
from utils.logger_config import configure_logger
from utils.utils import send_on_error_message

logger = configure_logger()


async def clear_cron_jobs(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for clear_cron_jobs")
        await send_on_error_message(context)
        return

    if context.job_queue is None:
        logger.error("context.job_queue is None for update_cron_jobs")
        await send_on_error_message(context)
        return

    for job in context.job_queue.jobs():
        job.schedule_removal()
        logger.info(f"Job {job} removed")
