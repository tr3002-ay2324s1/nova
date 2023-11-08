from datetime import time
from os import getenv
import pytz

NEW_YORK_TIMEZONE_INFO = pytz.timezone("America/New_York")
DAY_START_TIME = time(hour=8, minute=0, second=0)
DAY_END_TIME = time(hour=19, minute=0, second=0)
GOOGLE_CAL_BASE_URL = "https://calendar.google.com/calendar/u/0/r"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "email",
    "profile",
]
_ENV = getenv("ENVIRONMENT")  # "dev" or "prod"
BASE_URL = "http://127.0.0.1:8000" if _ENV == "dev" else "https://avon-seven.vercel.app"
TELEGRAM_BOT_LINK = "https://www.t.me/brio_tracker_bot"
