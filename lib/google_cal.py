from enum import Enum
from re import L
from typing import Any, Dict, List, Literal, Optional, Sequence, TypedDict, Union
from google_auth_oauthlib.flow import Flow
from datetime import datetime
from os import getenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.constants import BASE_URL, GOOGLE_CAL_BASE_URL, GOOGLE_SCOPES


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


class GoogleCalendarEventStatus(Enum):
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


class GoogleCalendarEventVisibility(Enum):
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
    private: Dict[Literal["nova_type"], NovaEvent] # This is how we store the type of event
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

class GoogleCalendarCreateEvent(TypedDict):
    kind: Literal["calendar#event"]
    etag: Optional[str]
    id: Optional[str]
    status: Optional[GoogleCalendarEventStatus]
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
    visibility: Optional[GoogleCalendarEventVisibility]
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


async def get_google_login_url(state_dict_str: Optional[str]):
    flow = Flow.from_client_config(
        client_config=get_google_oauth_client_config(),
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
        state=state_dict_str or "",
    )

    return authorization_url, state


def get_readable_cal_event_str(events: Sequence[GoogleCalendarReceivedEvent]):
    event_summary_strs = []
    for event in events:
        if "start" in event and "dateTime" in event.get("start"):
            # Guaranteed to be present because of if else
            event_datetime_str: str = event["start"]["dateTime"]  # type: ignore
            event_summary_strs.append(
                str(
                    event.get("summary")
                    + " @ "
                    + datetime.strptime(
                        event_datetime_str,
                        "%Y-%m-%dT%H:%M:%S%z",
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
    events: List[GoogleCalendarReceivedEvent] = events_result.get(
        "items", []
    )

    if type(events) is not list or len(events) == 0:
        print("No upcoming events found.")
        return []
    else:
        return events


def add_calendar_event(
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

    start_obj: GoogleCalendarEventTiming = {
        "timeZone": "America/New_York",
        "dateTime": start_time.isoformat(),
        "date": None,
    }
    end_obj: GoogleCalendarEventTiming = {
        "timeZone": "America/New_York",
        "dateTime": end_time.isoformat(),
        "date": None,
    }

    event: GoogleCalendarCreateEvent = {
        "summary": summary,
        "start": start_obj,
        "end": end_obj,
        "attendees": [],
        "eventType": "default",
        "anyoneCanAddSelf": False,
        "guestsCanInviteOthers": False,
        "guestsCanModify": False,
        "attachments": [],
        "attendeesOmitted": False,
        "colorId": None,
        "conferenceData": None,
        "created": None,
        "creator": None,
        "endTimeUnspecified": False,
        "etag": None,
        "extendedProperties": {
            "private": {
                "nova_type": event_type,
            },
            "shared": {},
        },
        "gadget": None,
        "guestsCanSeeOtherGuests": False,
        "description": None,
        "hangoutLink": None,
        "htmlLink": None,
        "iCalUID": None,
        "id": None,
        "kind": "calendar#event",
        "locked": False,
        "location": None,
        "organizer": None,
        "originalStartTime": None,
        "privateCopy": False,
        "recurrence": [],
        "recurringEventId": None,
        "reminders": None,
        "sequence": None,
        "source": None,
        "status": GoogleCalendarEventStatus.CONFIRMED,
        "transparency": None,
        "updated": None,
        "visibility": GoogleCalendarEventVisibility.PRIVATE,
        "workingLocationProperties": None,
    }

    event = service.events().insert(calendarId="primary", body=event).execute()


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


# async def find_next_available_time_slot(
#         refresh_token: str
#         events: Sequence[GoogleCalendarEvent],
#         event_duration_minutes: int
# ):
#     CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
#     CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
#     creds = Credentials.from_authorized_user_info(
#         info={
#             "refresh_token": refresh_token,
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#         },
#         scopes=GOOGLE_SCOPES,
#     )

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#     service = build('calendar', 'v3', credentials=creds)

#     # Get the current date and time
#     current_datetime = datetime.now(tz=pytz.timezone("America/New_York"))
#     current_date = current_datetime.date()
#     end_of_day = datetime.combine(current_date, datetime.time(datetime(year=current_date.year, month=current_date.month, day=current_date.day,hour=23, minute=59, second=59)))

#     # List events on the current day
#     events_result = service.events().list(
#         calendarId="primary",
#         timeMin=current_datetime.isoformat(),
#         timeMax=end_of_day.isoformat(),
#         singleEvents=True,
#     ).execute()
#     events = events_result.get('items', [])

#     # Loop from current time, in intervals of 15 mins, check scheduling conflict, if conflict continue, else return this time slot and don't allow event to be past 11:59pm
#     time_slot = current_datetime
#     # O(n^2) time complexity but n is small so it's fine
#     while time_slot < end_of_day:
#         # Check if there is a scheduling conflict
#         def is_scheduling_conflict(
#                 start_time: datetime,
#                 end_time: datetime,
#                 events: Sequence[GoogleCalendarEvent],
#         ):
#             for event in events:
#                 if event.get("start") and event.get("end") and event.get("start").get("dateTime") and event.get("end").get("dateTime"):
#                     event_start_time = datetime.fromisoformat(event.get("start").get("dateTime")) # type: ignore
#                     event_end_time = datetime.fromisoformat(event.get("end").get("dateTime")) # type: ignore
#                     if start_time < event_end_time or end_time > event_start_time:
#                         return True
#             return False

#         if not is_scheduling_conflict(time_slot, time_slot + timedelta(minutes=event_duration_minutes), events):
#             return time_slot
#         else:
#             time_slot += timedelta(minutes=15)
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
