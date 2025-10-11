from datetime import datetime, timezone

from config import (
    MAX_TASK_LENGTH, MAX_RESULTS_TO_FETCH_PER_CALENDAR,
    TOKEN_PATH, CREDENTIALS_PATH,
    LOG_FILE_PATH
)


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

from loguru import logger
from loguru import logger
logger.add(LOG_FILE_PATH)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SECRETS_DIR = BASE_DIR / "secrets"
TOKEN_PATH = SECRETS_DIR / "token.json"
CREDENTIALS_PATH = SECRETS_DIR / "credentials.json"

def get_credentials():
    """Obtain valid Google API credentials, refreshing or reauthenticating as needed."""
    logger.debug("Starting credential retrieval process.")
    creds = None

    # Load from file if exists
    if TOKEN_PATH.exists():
        logger.debug(f"Loading credentials from {TOKEN_PATH}")
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    else:
        logger.debug("No existing token file found.")

    # Check validity
    if creds and creds.valid:
        logger.debug("Existing credentials are valid; using cached token.")
        return creds
    
    logger.debug("Credentials are invalid or missing.")
    try:
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Attempting to refresh expired credentials.")
            creds.refresh(Request())
            logger.info("Token refreshed successfully.")
        else:
            logger.debug("No valid refresh token available; initiating new auth flow.")
            raise RefreshError()
    except RefreshError as e:
        logger.warning(f"Refresh failed ({e}); starting browser-based reauthentication.")
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES
        )
        creds = flow.run_local_server(port=0)
        logger.info("User successfully reauthenticated via browser flow.")

    # Save updated credentials
    with TOKEN_PATH.open("w") as token:
        token.write(creds.to_json())
        logger.debug(f"Credentials saved to {TOKEN_PATH}")

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
    logger.info('Running fetch.py directly; fetching and printing current event names.')
    print(fetch_current_event_names())
    logger.info('fetch.py finished running.')