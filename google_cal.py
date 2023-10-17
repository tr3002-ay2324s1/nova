from enum import Enum
from typing import Dict, List, Optional, Sequence, Type, TypedDict, Union
from google_auth_oauthlib.flow import Flow
from datetime import timedelta, datetime
from os import getenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import pytz

from telegram import Update
from telegram.ext import ContextTypes

from constants import BASE_URL, GOOGLE_SCOPES
from database import fetch_user
from job_queue import add_once_job
from morning_flow import morning_flow_event


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
            str(
                event["summary"]
                + " @ "
                + datetime.strptime(
                    event["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z"
                ).strftime("%H:%M %z")
            )
            + "\n"
            for event in events
        ]
    )

def get_calendar_events(
    *,
    refresh_token,
    timeMin=datetime.utcnow().isoformat() + "Z",  # 'Z' indicates UTC time
    timeMax=None,
    k=10,
):  # -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:# -> list[Any] | Any | List[GoogleCalendarEvent]:
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
    print("Getting the upcoming k events")
    events_result = (
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
    events: List[GoogleCalendarEvent] = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return []
    else:
        for event in events:
            start = event.get("start").get("dateTime", event.get("start").get("date"))
            end = (
                event.get("end").get("dateTime", event.get("end").get("date"))
                if not event.get("endTimeUnspecified", False)
                else None
            )
            if not start:
                continue
            else:
                print(start, end, event["summary"])
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
    print("START",start_obj)
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

async def refresh_daily_jobs_with_google_cal(update: Optional[Update], user_id: Optional[str], context: ContextTypes.DEFAULT_TYPE):
    users = fetch_user(telegram_user_id=(update.message.from_user.id) or user_id)
    first_user = users[0]
    refresh_token = first_user.get("google_refresh_token", "")
    # Get events from tomorrow 12am to tomorrow 11:59pm
    today = datetime.utcnow()
    today_midnight = datetime(today.year, today.month, today.day, 0, 0)
    events = get_calendar_events(
        refresh_token=refresh_token,
        timeMin=today_midnight.isoformat() + "Z",
        timeMax=(today_midnight + timedelta(days=1)).isoformat() + "Z",
        k=20,
    )
    for e in events:
        # Create a datetime object for the current datetime
        current_datetime = datetime.now(tz=pytz.timezone("America/New_York"))
        # Create a datetime object for the given datetime
        if e.get("start").get("date"):
            continue
        given_datetime = datetime.fromisoformat(e.get("start").get("dateTime", ""))
        if not given_datetime:
            continue
        # Calculate the time difference in seconds
        time_diff = (current_datetime - given_datetime).total_seconds()
        chat_id = update.message.chat_id or update.effective_chat.id or -1
        await add_once_job(job=morning_flow_event, due=time_diff, chat_id=chat_id, context=context)
    return [e for e in events]
