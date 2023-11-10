from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union
from typing_extensions import TypedDict
from datetime import datetime, time, timedelta
from os import getenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.constants import (
    GOOGLE_CAL_BASE_URL,
    GOOGLE_SCOPES,
    NEW_YORK_TIMEZONE_INFO,
)


class NovaEvent(str, Enum):
    EVENT = "event"
    HABIT = "habit"
    TASK = "task"


class GoogleOauthClientConfig(TypedDict):
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: List[str]
    javascript_origins: List[str]


class GoogleCalendarEventStatus(str, Enum):
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class GoogleCalendarCreateEventReminderOverride(TypedDict):
    method: str
    minutes: int


class GoogleCalendarCreateEventAttachment(TypedDict):
    fileUrl: str
    title: str
    mimeType: str
    iconLink: str
    fileId: str


class GoogleCalendarCreateEventReminder(TypedDict):
    useDefault: bool
    overrides: List[GoogleCalendarCreateEventReminderOverride]


class GoogleCalendarCreateEventGadget(TypedDict):
    type: str
    title: str
    link: str
    iconLink: str
    width: int
    height: int
    display: str
    preferences: Dict[str, str]


class GoogleCalendarEventVisibility(str, Enum):
    DEFAULT = "default"
    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


class GoogleCalendarEventTiming(TypedDict):
    dateTime: Optional[str]  # ISO 8601
    date: Optional[str]  # ISO 8601
    timeZone: str


class GoogleCalendarEventWorkingLocationType(Enum):
    HOME_OFFICE = "homeOffice"
    CUSTOM_LOCATION = "customLocation"
    OFFICE_LOCATION = "officeLocation"


class GoogleCalendarEventWorkingLocationOfficeLocation(TypedDict):
    buildingId: str
    floorId: str
    floorSectionId: str
    deskId: str
    label: str


class GoogleCalendarEventWorkingLocation(TypedDict):
    type: GoogleCalendarEventWorkingLocationType
    homeOffice: Any  # If present, user is working from home
    customLocation: Dict[Literal["label"], str]
    officeLocation: GoogleCalendarEventWorkingLocationOfficeLocation


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


class GoogleCalendarCreateEventConferenceDataCreateRequest(TypedDict):
    requestId: str
    conferenceSolutionKey: Dict[Literal["type"], str]
    status: Dict[Literal["statusCode"], str]


class GoogleCalendarCreateEventConferenceDataEntryPoint(TypedDict):
    entryPointType: str
    uri: str
    label: str
    pin: str
    accessCode: str
    meetingCode: str
    passcode: str
    password: str


class GoogleCalendarCreateEventConferenceDataConferenceSolution(TypedDict):
    key: Dict[Literal["type"], str]
    name: str
    iconUri: str


class GoogleCalendarCreateEventConferenceData(TypedDict):
    createRequest: GoogleCalendarCreateEventConferenceDataCreateRequest
    entryPoints: List[GoogleCalendarCreateEventConferenceDataEntryPoint]
    conferenceSolution: GoogleCalendarCreateEventConferenceDataConferenceSolution
    conferenceId: str
    signature: str
    notes: str


class GoogleCalendarCreateEventExtendedProperties(TypedDict):
    private: Dict[
        Literal["nova_type"], NovaEvent
    ]  # This is how we store the type of event
    shared: Dict[str, str]


class GoogleCalendarReceivedEvent(TypedDict):
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
    extendedProperties: Optional[GoogleCalendarCreateEventExtendedProperties]


class GoogleCalendarEventMinimum(TypedDict):
    start: GoogleCalendarEventTiming
    end: GoogleCalendarEventTiming
    summary: str


class GoogleCalendarCreateEvent(TypedDict):
    kind: Literal["calendar#event"]
    etag: Optional[str]
    id: Optional[str]
    status: Optional[str]
    htmlLink: Optional[str]
    created: Optional[datetime]
    updated: Optional[datetime]
    summary: str
    description: Optional[str]
    location: Optional[str]
    colorId: Optional[str]
    creator: Optional[GoogleCalendarPerson]
    organizer: Optional[GoogleCalendarPerson]
    start: GoogleCalendarEventTiming
    end: GoogleCalendarEventTiming
    endTimeUnspecified: Optional[bool]
    recurrence: Optional[List[str]]
    recurringEventId: Optional[str]
    originalStartTime: Optional[GoogleCalendarEventTiming]
    transparency: Optional[str]
    visibility: Optional[str]
    iCalUID: Optional[str]
    sequence: Optional[int]
    attendees: Optional[List[GoogleCalendarAttendee]]
    attendeesOmitted: Optional[bool]
    extendedProperties: Optional[GoogleCalendarCreateEventExtendedProperties]
    hangoutLink: Optional[str]
    conferenceData: Optional[GoogleCalendarCreateEventConferenceData]
    gadget: Optional[GoogleCalendarCreateEventGadget]
    anyoneCanAddSelf: Optional[bool]
    guestsCanInviteOthers: Optional[bool]
    guestsCanModify: Optional[bool]
    guestsCanSeeOtherGuests: Optional[bool]
    privateCopy: Optional[bool]
    locked: Optional[bool]
    reminders: Optional[List[GoogleCalendarCreateEventReminder]]
    source: Optional[Dict[Union[Literal["url"], Literal["title"]], str]]
    workingLocationProperties: Optional[GoogleCalendarEventWorkingLocation]
    attachments: Optional[List[GoogleCalendarCreateEventAttachment]]
    eventType: Optional[
        Union[
            Literal["default"],
            Literal["outOfOffice"],
            Literal["workingLocation"],
            Literal["focusTime"],
        ]
    ]


class GoogleCalendarGetEventsResponse(TypedDict):
    items: List[GoogleCalendarReceivedEvent]


def get_google_oauth_client_config() -> Dict[str, GoogleOauthClientConfig]:
    client_id = getenv("GOOGLE_CLIENT_ID")
    client_secret = getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise Exception("GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is not set")
    client_config: GoogleOauthClientConfig = {
        "client_id": client_id,
        "project_id": "nova-401105",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": client_secret,
        "redirect_uris": ["http://127.0.0.1:8000/google_oauth_callback"],
        "javascript_origins": ["http://localhost:8081"],
    }

    return {"web": client_config}


def get_google_cal_link(telegram_user_id: Optional[int]):
    # Get user data from DB and re-direct to their calendar ID
    user_data = None

    if user_data:
        return f"{GOOGLE_CAL_BASE_URL}?cid={telegram_user_id}"
    else:
        return GOOGLE_CAL_BASE_URL


def get_readable_cal_event_str(events: Sequence[GoogleCalendarEventMinimum]):
    event_summary_strs = []
    for event in events:
        if "start" in event and "dateTime" in event.get("start"):
            event_datetime_str: str = event["start"]["dateTime"]  # type: ignore
            event_summary_strs.append(
                str(
                    event.get("summary")
                    + " @ "
                    + datetime.strptime(
                        event_datetime_str,
                        "%Y-%m-%dT%H:%M:%S.%f%z",
                    ).strftime("%H:%M")
                )
            )
    return "\n".join(event_summary_strs)


def get_calendar_events(
    *,
    refresh_token,
    timeMin=datetime.utcnow().isoformat() + "Z",  # 'Z' indicates UTC time
    timeMax=None,
    k=10,
) -> List[
    GoogleCalendarReceivedEvent
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
    events: List[GoogleCalendarReceivedEvent] = events_result.get("items", [])

    if type(events) is not list or len(events) == 0:
        print("No upcoming events found.")
        return []
    else:
        return events


def add_calendar_item(
    *,
    refresh_token: str,
    summary: str,
    start_time: datetime,
    end_time: datetime,
    event_type: NovaEvent,
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
        "timeZone": "America/New_York",
        "dateTime": start_time.isoformat(),
    }
    end_obj = {
        "timeZone": "America/New_York",
        "dateTime": end_time.isoformat(),
    }

    event = {
        "summary": summary,
        "start": start_obj,
        "end": end_obj,
        "extendedProperties": {
            "private": {
                "nova_type": event_type.value,
            },
            "shared": {},
        },
    }

    event_res = service.events().insert(calendarId="primary", body=event).execute()


def update_calendar_event(
    *,
    event_id: str,
    refresh_token: str,
    updated_event: GoogleCalendarCreateEvent,
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

    updated_event = (
        service.events()
        .update(calendarId="primary", eventId=event_id, body=updated_event)
        .execute()
    )


def merge_events(
    events: Sequence[GoogleCalendarReceivedEvent],
) -> List[GoogleCalendarReceivedEvent]:
    """
    Merge overlapping events to simplify conflict checking
    """
    # Merge overlapping events to simplify conflict checking
    sorted_events = sorted(
        events,
        key=lambda e: datetime.fromisoformat(
            e["start"].get(
                "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat()
            )
        ),
    )
    merged_events = []
    for event in sorted_events:
        if not merged_events or datetime.fromisoformat(
            merged_events[-1]["end"].get(
                "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
            )
        ) <= datetime.fromisoformat(
            event["start"].get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO))
        ):
            merged_events.append(event)
        else:
            merged_events[-1]["end"]["dateTime"] = max(
                datetime.fromisoformat(
                    merged_events[-1]["end"].get(
                        "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
                    )
                ),
                datetime.fromisoformat(
                    event["end"].get(
                        "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
                    )
                ),
            ).isoformat()
    return merged_events


START_BUSINESS_TIME = time(8, 0)
END_BUSINESS_TIME = time(18, 0)


def is_within_business_hours(check_time: datetime) -> bool:
    """Check if the time is within the business hours."""
    return START_BUSINESS_TIME <= check_time.time() < END_BUSINESS_TIME


def find_next_available_time_slot(
    refresh_token: str,
    time_min: datetime,
    time_max: datetime,
    event_duration_minutes: int,
) -> Optional[Tuple[datetime, datetime]]:
    events = get_calendar_events(
        refresh_token=refresh_token,
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        k=500,
    )

    # Preprocess events to merge overlapping ones
    merged_events = merge_events(events)

    # Adjust start time to be within business hours if necessary
    if time_min.time() < START_BUSINESS_TIME:
        available_start = datetime.combine(time_min.date(), START_BUSINESS_TIME)
    elif time_min.time() >= END_BUSINESS_TIME:
        next_day = time_min.date() + timedelta(days=1)
        available_start = datetime.combine(next_day, START_BUSINESS_TIME)
    else:
        available_start = time_min

    for event in merged_events:
        event_start = datetime.fromisoformat(
            event["start"].get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO))
        )
        event_end = datetime.fromisoformat(
            event["end"].get("dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO))
        )

        # Check if there is enough time before this event starts
        potential_end = available_start + timedelta(minutes=event_duration_minutes)
        if (
            potential_end <= event_start
            and is_within_business_hours(potential_end)
            and potential_end <= time_max
        ):
            return available_start, potential_end

        # Move the available start to the end of the current event if it overlaps
        if available_start < event_end:
            available_start = event_end
            # If the event ends after business hours, move to the start of the next business day
            if not is_within_business_hours(available_start):
                next_day = available_start.date() + timedelta(days=1)
                available_start = datetime.combine(next_day, START_BUSINESS_TIME)

    # Final check if there is enough time after the last event before time_max
    if available_start + timedelta(
        minutes=event_duration_minutes
    ) <= time_max and is_within_business_hours(available_start):
        return available_start, available_start + timedelta(
            minutes=event_duration_minutes
        )

    # If no slot is found, return None
    return None


# async def find_next_available_time_slot(
#     refresh_token: str,
#     time_min: datetime,
#     time_max: datetime,
#     event_duration_minutes: int,
# ):
#     events = get_calendar_events(
#         refresh_token=refresh_token,
#         timeMin=time_min.isoformat(),
#         timeMax=time_max.isoformat(),
#         k=500,
#     )

#     raise Exception(json.dumps(events))

#     # Loop from minimum time
#     curr = time_min
#     # O(n^2) time complexity but n is small so it's fine
#     while curr < time_max:
#         # Check if there is a scheduling conflict
#         def is_scheduling_conflict(
#             start_time: datetime,
#             end_time: datetime,
#             events: Sequence[GoogleCalendarReceivedEvent],
#         ):
#             for event in events:
#                 if (
#                     event.get("start")
#                     and event.get("end")
#                     and event.get("start").get("dateTime")
#                     and event.get("end").get("dateTime")
#                 ):
#                     event_start_time = datetime.fromisoformat(event.get("start").get("dateTime"))  # type: ignore
#                     event_end_time = datetime.fromisoformat(event.get("end").get("dateTime"))  # type: ignore
#                     if start_time < event_end_time or end_time > event_start_time:
#                         return True
#             return False

#         if not is_scheduling_conflict(
#             curr, curr + timedelta(minutes=event_duration_minutes), events
#         ):
#             return curr, curr + timedelta(minutes=event_duration_minutes)
#         else:
#             curr += timedelta(minutes=event_duration_minutes)
#     return None


# async def refresh_daily_jobs_with_google_cal(
#     context: ContextTypes.DEFAULT_TYPE,
#     get_next_event_job: Callable[[datetime, str Optional[datetime]], Callable[
#         ..., Coroutine[Any, Any, None]
#     ]],  # curried function that takes in event time and desc and returns job function
# ) -> List[GoogleCalendarEvent]:
#     if context.chat_data is None:
#         logger.error("context.chat_data is None for refresh_daily_jobs_with_google_cal")
#         await send_on_error_message(context)
#         return []
#     user_id = context.chat_data["user_id"]
#     chat_id = context.chat_data["chat_id"]
#     users = fetch_user(telegram_user_id=user_id)
#     first_user = users[0]
#     refresh_token = first_user.get("google_refresh_token", "")

#     # Get events from tomorrow 12am to tomorrow 11:59pm
#     today = datetime.now(
#         tz=pytz.timezone("America/New_York")
#         )
#     today_midnight = datetime(today.year, today.month, today.day, 23, 30)
#     events = get_calendar_events(
#         refresh_token=refresh_token,
#         timeMin=today_midnight.isoformat() + "Z",
#         timeMax=(today_midnight + timedelta(days=1)).isoformat() + "Z",
#         k=20,
#     )
#     logger.info("refreshed cal", events)
#     for event in events:
#         # Create a datetime object for the current datetime
#         current_datetime = datetime.now(tz=pytz.timezone("America/New_York"))
#         # Create a datetime object for the given datetime
#         if not event.get("start").get("dateTime", False):
#             # Skip all-day events
#             continue
#         given_datetime = datetime.fromisoformat(
#             event.get("start").get("dateTime", "")
#         )
#         if not given_datetime:
#             continue
#         # Calculate the time difference in seconds
#         time_diff = (current_datetime - given_datetime).total_seconds()

#         has_end_datetime = event.get("endTimeUnspecified", False)
#         end_datetime = datetime.fromisoformat(
#             event.get("end").get("dateTime", "")
#         ) if has_end_datetime else None

#         job_func = get_next_event_job(given_datetime, event.get("summary"), end_datetime)

#         await add_once_job(
#             job=job_func, due=time_diff, chat_id=chat_id, context=context
#         )
#     return events
