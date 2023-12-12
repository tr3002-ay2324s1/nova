from telegram.ext import ContextTypes
from utils.logger_config import configure_logger
from utils.utils import send_on_error_message

logger = configure_logger()


async def add_night_flow(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data is None:
        logger.error("context.chat_data is None for add_morning_flow")
        await send_on_error_message(context)
        return

    from flows.night_flow import night_flow_review
    from utils.constants import NIGHT_FLOW_TIME
    from utils.job_queue import add_daily_job

    # add back night flow
    await add_daily_job(
        callback=night_flow_review,
        time=NIGHT_FLOW_TIME,
        chat_id=context.chat_data["chat_id"],
        context=context,
    )
