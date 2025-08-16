from datetime import datetime, timezone

from config import (
    MAX_TASK_LENGTH, MAX_RESULTS_TO_FETCH_PER_CALENDAR,
    TOKEN_PATH, CREDENTIALS_PATH,
    LOG_FILE_PATH
)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.credentials import Credentials as CredentialsType  # for typechecking
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar']

from loguru import logger
logger.add(LOG_FILE_PATH)

def save_credentials(creds):
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())

def get_credentials_online():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def get_credentials():
    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            logger.warning(f"Failed to load credentials from token file: {e}")
            TOKEN_PATH.unlink(missing_ok=True)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Refresh token failed: {e}. Re-authenticating.")
                TOKEN_PATH.unlink(missing_ok=True)
                creds = get_credentials_online()
        else:
            creds = get_credentials_online()
        
        save_credentials(creds)

    return creds

def parse_event_datetime(event_time: dict) -> datetime | None:
    if "dateTime" in event_time:
        # Offset-aware datetime with timezone info
        return datetime.fromisoformat(event_time["dateTime"])
    elif "date" in event_time:
        # All-day event → do nothing.
        return None
    else:
        raise ValueError(f"Unexpected event time format: {event_time}")

def fetch_current_event_names_from_calendar(service, calendar_id) -> list[str]:
    utc_now = datetime.now(timezone.utc)
    try:
        events_response = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=(utc_now - MAX_TASK_LENGTH).isoformat(),
                timeMax=(utc_now + MAX_TASK_LENGTH).isoformat(),
                maxResults=MAX_RESULTS_TO_FETCH_PER_CALENDAR,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError as error:
        logger.error(f"Error fetching calendar items: {error}")
        return []
    
    event_objects = events_response.get('items', None)
    if event_objects is None:
        logger.error(f"The returned dictionary did not have an items attribute despite no HttpErrors. Shouldn't be possible.")
        return []
    
    current_event_names = []
    for event in event_objects:
        start = parse_event_datetime(event["start"])
        end = parse_event_datetime(event["end"])
        if not start or not end:
            continue
        if start <= utc_now < end:
            current_event_names.append(event["summary"])
    
    return current_event_names

def fetch_current_event_names() -> list[str]:
    logger.info('Fetching current event names...')
    service = build('calendar', 'v3', credentials=get_credentials())
    calendar_list = service.calendarList().list().execute()
    calendar_ids = [calendar['id'] for calendar in calendar_list.get('items', [])]

    current_events = []
    for calendar_id in calendar_ids:
        current_events.extend(fetch_current_event_names_from_calendar(service, calendar_id))
    logger.info('Fetched event names.')
    return current_events

if __name__ == '__main__': # Not meant to be run directly but if it is...
    logger.info(fetch_current_event_names())