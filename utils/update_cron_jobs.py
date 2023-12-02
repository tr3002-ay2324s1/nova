from telegram.ext import ContextTypes
from utils.logger_config import configure_logger
from utils.utils import send_on_error_message

logger = configure_logger()


async def update_cron_jobs(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for update_cron_jobs")
        await send_on_error_message(context)
        return

    from utils.add_block_flows import add_block_flows
    from utils.add_morning_flow import add_morning_flow
    from utils.job_queue import clear_cron_jobs

    await clear_cron_jobs(context)

    await add_morning_flow(context)

    await add_block_flows(context)
