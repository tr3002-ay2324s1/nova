from datetime import datetime, time, timedelta
from os import getenv
import pytz

NEW_YORK_TIMEZONE_INFO = pytz.timezone("America/New_York")
DAY_START_TIME = time(hour=8, minute=0, second=0, tzinfo=NEW_YORK_TIMEZONE_INFO)
# DAY_START_TIME = (datetime.now(tz=NEW_YORK_TIMEZONE_INFO) + timedelta(seconds=20)).time()
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
READYMADE_RESPONSES = [
    "Embrace the glorious mess that you are and get stuff done!",
    "Progress, not perfection. Just do your best and keep going.",
    "Coffee in one hand, confidence in the other - let's be productive!",
    "Life is too short for long to-do lists. Focus on what truly matters.",
    "You got this! Take a deep breath, enjoy the journey, and make things happen.",
]
