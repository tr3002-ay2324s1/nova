from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union
from typing_extensions import TypedDict
from datetime import datetime, timedelta
from os import getenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.constants import (
    DAY_END_TIME,
    DAY_START_TIME,
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
    summary: str  # Always there
    description: str  # Not always there
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
                        event_datetime_str, "%Y-%m-%dT%H:%M:%S%z"
                    ).strftime("%H:%M")
                )
            )
    return "\n".join(event_summary_strs) or "No upcoming events found."


def get_calendar_events(
    *,
    refresh_token,
    q: Optional[
        str
    ] = None,  # Query string for calendar name, summary, description, etc.
    timeMin: Optional[str] = datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat(),
    timeMax: Optional[str] = (
        datetime.now(tz=NEW_YORK_TIMEZONE_INFO) + timedelta(days=30)
    ).isoformat(),
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
    if not timeMin and not timeMax and not q:
        print("Time min or time max or q not set")
        return []
    events_result: GoogleCalendarGetEventsResponse = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=k,
            q=q,
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


def get_google_cal_service(refresh_token: str):
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
    return service


def add_calendar_item(
    *,
    refresh_token: str,
    summary: str,
    start_time: datetime,
    end_time: datetime,
    event_type: NovaEvent,
):
    service = get_google_cal_service(refresh_token)

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


def add_recurring_calendar_item(
    *,
    refresh_token: str,
    summary: str,
    start_time: datetime,
    end_time: datetime,
    rrules: List[str],
):
    service = get_google_cal_service(refresh_token)
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
        "recurrence": rrules,
        "extendedProperties": {
            "private": {
                "nova_type": NovaEvent.HABIT.value,
            },
            "shared": {},
        },
    }

    recurring_event = (
        service.events().insert(calendarId="primary", body=event).execute()
    )


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


def sort_events(
    events: Sequence[GoogleCalendarEventMinimum],
) -> List[GoogleCalendarEventMinimum]:
    return sorted(
        events,
        # Sort by start time in ascending order
        key=lambda e: datetime.fromisoformat(
            e["start"].get(
                "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat()
            )
        ),
    )


def merge_events(
    events: Sequence[GoogleCalendarEventMinimum],
) -> List[GoogleCalendarEventMinimum]:
    """
    Merge overlapping events to simplify conflict checking
    """
    # Merge overlapping events to simplify conflict checking
    sorted_events = sort_events(events)
    merged_events: List[GoogleCalendarEventMinimum] = []
    for event in sorted_events:
        has_merged_events = bool(merged_events and len(merged_events) > 0)
        if not has_merged_events or (
            event.get("start").get("dateTime")
            and (
                datetime.fromisoformat(
                    merged_events[-1]
                    .get("end")
                    .get(
                        "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat()
                    )
                )
                <= datetime.fromisoformat(
                    event.get("start").get(
                        "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat()
                    )
                )
            )
        ):
            merged_events.append(event)
        else:
            merged_events[-1]["end"]["dateTime"] = max(
                datetime.fromisoformat(
                    merged_events[-1]["end"].get(
                        "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat()
                    )
                ),
                datetime.fromisoformat(
                    event["end"].get(
                        "dateTime", datetime.now(tz=NEW_YORK_TIMEZONE_INFO).isoformat()
                    )
                ),
            ).isoformat()
    return merged_events


def is_within_business_hours(check_time: datetime) -> bool:
    """Check if the time is within the business hours."""
    return DAY_START_TIME <= check_time.time() < DAY_END_TIME


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
    if time_min.time() < DAY_START_TIME:
        available_start = datetime.combine(
            time_min.date(), DAY_START_TIME, tzinfo=NEW_YORK_TIMEZONE_INFO
        )
    elif time_min.time() >= DAY_END_TIME:
        next_day = time_min.date() + timedelta(days=1)
        available_start = datetime.combine(
            next_day, DAY_END_TIME, tzinfo=NEW_YORK_TIMEZONE_INFO
        )
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
                available_start = datetime.combine(
                    next_day, DAY_START_TIME, tzinfo=NEW_YORK_TIMEZONE_INFO
                )

    # Final check if there is enough time after the last event before time_max
    if available_start + timedelta(
        minutes=event_duration_minutes
    ) <= time_max and is_within_business_hours(available_start):
        return available_start, available_start + timedelta(
            minutes=event_duration_minutes
        )

    # If no slot is found, return None
    return None
