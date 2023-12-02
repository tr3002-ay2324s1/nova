from telegram.ext import ContextTypes
from utils.logger_config import configure_logger
from utils.utils import send_on_error_message

logger = configure_logger()


async def add_morning_flow(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for add_morning_flow")
        await send_on_error_message(context)
        return

    from flows.morning_flow import morning_flow
    from utils.constants import DAY_START_TIME
    from utils.job_queue import add_daily_job

    # add back morning flow
    await add_daily_job(
        callback=morning_flow,
        time=DAY_START_TIME,
        chat_id=context.chat_data["chat_id"],
        context=context,
    )
