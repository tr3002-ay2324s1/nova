from enum import Enum
from typing import Any, Callable, Coroutine, List, Optional, Sequence, TypedDict, Union
from google_auth_oauthlib.flow import Flow
from datetime import timedelta, datetime
from os import getenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import pytz
from telegram.ext import ContextTypes
from logger_config import configure_logger
from constants import BASE_URL, GOOGLE_SCOPES
from database import fetch_user
from job_queue import add_once_job
from utils import send_on_error_message

logger = configure_logger()


class GoogleCalendarEventStatus(Enum):
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class GoogleCalendarEventVisibility(Enum):
    DEFAULT = "default"
    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


class GoogleCalendarEventTiming(TypedDict):
    dateTime: Optional[str]  # ISO 8601
    date: Optional[str]  # ISO 8601
    timeZone: str


class GoogleCalendarPerson(TypedDict):
    id: str
    self: bool
    displayName: str
    email: str


class GoogleCalendarAttendee(GoogleCalendarPerson):
    responseStatus: str
    comment: str
    optional: bool
    resource: bool


class GoogleCalendarEvent(TypedDict):
    start: GoogleCalendarEventTiming
    originalStartTime: GoogleCalendarEventTiming
    end: GoogleCalendarEventTiming
    endTimeUnspecified: bool
    summary: str
    description: str
    status: GoogleCalendarEventStatus
    id: str
    creator: GoogleCalendarPerson
    organizer: GoogleCalendarPerson
    visibility: GoogleCalendarEventVisibility
    created: datetime
    updated: datetime
    htmlLink: str
    attendees: List[GoogleCalendarAttendee]


class GoogleCalendarGetEventsResponse(TypedDict):
    items: List[GoogleCalendarEvent]


async def get_login_google(telegram_user_id: int, username: str):
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": getenv("GOOGLE_CLIENT_ID"),
                "project_id": "nova-401105",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": ["http://127.0.0.1:8000/google_oauth_callback"],
                "javascript_origins": ["http://localhost:8000"],
            }
        },
        scopes=GOOGLE_SCOPES,
    )

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = BASE_URL + "/google_oauth_callback"

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
        state=json.dumps(
            {"telegram_user_id": str(telegram_user_id), "username": username}
        ),
    )

    return authorization_url, state


def get_readable_cal_event_string(events: Sequence[GoogleCalendarEvent]):
    return "".join(
        [
            (
                str(
                    event.get("summary")
                    + " @ "
                    + datetime.strptime(
                        event.get("start").get(
                            "dateTime",
                            "",  # Guaranteed not to happen because of if else
                        ),
                        "%Y-%m-%dT%H:%M:%S%z",
                    ).strftime("%H:%M")
                )
                + "\n"
            )
            if "start" in event and "dateTime" in event.get("start")
            else ""
            for event in events
        ]
    )


def get_calendar_events(
    *,
    refresh_token,
    timeMin=datetime.utcnow().isoformat() + "Z",  # 'Z' indicates UTC time
    timeMax=None,
    k=10,
) -> List[
    GoogleCalendarEvent
]:  # -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:
    """Shows basic usage of the Google Calendar API."""
    CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
    creds = Credentials.from_authorized_user_info(
        info={
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        scopes=GOOGLE_SCOPES,
    )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    print(f"Getting the upcoming {k} events")
    events_result: GoogleCalendarGetEventsResponse = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=k,
            singleEvents=True,
            orderBy="startTime",
            timeZone="America/New_York",
        )
        .execute()
    )
    events: Union[List[GoogleCalendarEvent], None] = events_result.get("items", [])

    if events is None or type(events) is not list:
        print("No upcoming events found.")
        return []
    else:
        return events


def add_calendar_event(
    *,
    refresh_token,
    summary,
    start_time: datetime,
    end_time: datetime,
):
    CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
    creds = Credentials.from_authorized_user_info(
        info={
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        scopes=GOOGLE_SCOPES,
    )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    service = build("calendar", "v3", credentials=creds)

    start_obj = {
        # "date": start_time.date().isoformat(),
        "timeZone": "America/New_York",
        "dateTime": start_time.isoformat(),
    }
    print("START", start_obj)
    end_obj = {
        # "date": end_time.date().isoformat(),
        "timeZone": "America/New_York",
        "dateTime": end_time.isoformat(),
    }

    event = {
        "summary": summary,
        "start": start_obj,
        "end": end_obj,
    }

    event = service.events().insert(calendarId="primary", body=event).execute()

async def find_next_available_time_slot(
        refresh_token: str,
        events: Sequence[GoogleCalendarEvent],
        event_duration_minutes: int,
):
    CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
    creds = Credentials.from_authorized_user_info(
        info={
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        scopes=GOOGLE_SCOPES,
    )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    service = build('calendar', 'v3', credentials=creds)

    # Get the current date and time
    current_datetime = datetime.now(tz=pytz.timezone("America/New_York"))
    current_date = current_datetime.date()
    end_of_day = datetime.combine(current_date, datetime.time(datetime(year=current_date.year, month=current_date.month, day=current_date.day,hour=23, minute=59, second=59)))

    # List events on the current day
    events_result = service.events().list(
        calendarId="primary",
        timeMin=current_datetime.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
    ).execute()
    events = events_result.get('items', [])

    # Loop from current time, in intervals of 15 mins, check scheduling conflict, if conflict continue, else return this time slot and don't allow event to be past 11:59pm
    time_slot = current_datetime
    # O(n^2) time complexity but n is small so it's fine
    while time_slot < end_of_day:
        # Check if there is a scheduling conflict
        def is_scheduling_conflict(
                start_time: datetime,
                end_time: datetime,
                events: Sequence[GoogleCalendarEvent],
        ):
            for event in events:
                if event.get("start") and event.get("end") and event.get("start").get("dateTime") and event.get("end").get("dateTime"):
                    event_start_time = datetime.fromisoformat(event.get("start").get("dateTime")) # type: ignore
                    event_end_time = datetime.fromisoformat(event.get("end").get("dateTime")) # type: ignore
                    if start_time < event_end_time or end_time > event_start_time:
                        return True
            return False
        
        if not is_scheduling_conflict(time_slot, time_slot + timedelta(minutes=event_duration_minutes), events):
            return time_slot
        else:
            time_slot += timedelta(minutes=15)
    return None


async def refresh_daily_jobs_with_google_cal(
    context: ContextTypes.DEFAULT_TYPE,
    get_next_event_job: Callable[[datetime, str, Optional[datetime]], Callable[
        ..., Coroutine[Any, Any, None]
    ]],  # curried function that takes in event time and desc and returns job function
) -> List[GoogleCalendarEvent]:
    if context.chat_data is None:
        logger.error("context.chat_data is None for refresh_daily_jobs_with_google_cal")
        await send_on_error_message(context)
        return []
    user_id = context.chat_data["user_id"]
    chat_id = context.chat_data["chat_id"]
    users = fetch_user(telegram_user_id=user_id)
    first_user = users[0]
    refresh_token = first_user.get("google_refresh_token", "")

    # Get events from tomorrow 12am to tomorrow 11:59pm
    today = datetime.now(
        tz=pytz.timezone("America/New_York")
        )
    today_midnight = datetime(today.year, today.month, today.day, 23, 30)
    events = get_calendar_events(
        refresh_token=refresh_token,
        timeMin=today_midnight.isoformat() + "Z",
        timeMax=(today_midnight + timedelta(days=1)).isoformat() + "Z",
        k=20,
    )
    logger.info("refreshed cal", events)
    for event in events:
        # Create a datetime object for the current datetime
        current_datetime = datetime.now(tz=pytz.timezone("America/New_York"))
        # Create a datetime object for the given datetime
        if not event.get("start").get("dateTime", False):
            # Skip all-day events
            continue
        given_datetime = datetime.fromisoformat(
            event.get("start").get("dateTime", "")
        )
        if not given_datetime:
            continue
        # Calculate the time difference in seconds
        time_diff = (current_datetime - given_datetime).total_seconds()

        has_end_datetime = event.get("endTimeUnspecified", False)
        end_datetime = datetime.fromisoformat(
            event.get("end").get("dateTime", "")
        ) if has_end_datetime else None

        job_func = get_next_event_job(given_datetime, event.get("summary"), end_datetime)

        await add_once_job(
            job=job_func, due=time_diff, chat_id=chat_id, context=context
        )
    return events
