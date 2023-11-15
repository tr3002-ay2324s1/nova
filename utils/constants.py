from datetime import datetime, time, timedelta
from os import getenv
import pytz

NEW_YORK_TIMEZONE_INFO = pytz.timezone("America/New_York")
# DAY_START_TIME = time(hour=8, minute=0, second=0, tzinfo=NEW_YORK_TIMEZONE_INFO)
DAY_START_TIME = (datetime.now(tz=NEW_YORK_TIMEZONE_INFO) + timedelta(seconds=10)).time()
DAY_END_TIME = time(hour=19, minute=0, second=0, tzinfo=NEW_YORK_TIMEZONE_INFO)
GOOGLE_CAL_BASE_URL = "https://calendar.google.com/calendar/u/0/r"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events",
]
_ENV = getenv("ENVIRONMENT")  # "dev" or "prod"
BASE_URL = (
    "http://127.0.0.1:8000" if _ENV == "dev" else "https://nova-api-ten.vercel.app"
)
TELEGRAM_BOT_LINK = "https://www.t.me/brio_tracker_bot"
