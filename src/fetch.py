import concurrent.futures
from datetime import datetime, timezone

from config import (
    MAX_TASK_LENGTH, MAX_RESULTS_TO_FETCH_PER_CALENDAR,
    USER_ACCESS_CREDENTIALS_PATH, CLIENT_SECRETS_PATH,
    LOG_FILE_PATH,
    FETCH_TIMEOUT_SECONDS,
)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

from loguru import logger
logger.add(LOG_FILE_PATH)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

def save_user_credentials(user_creds):
    with USER_ACCESS_CREDENTIALS_PATH.open("w") as cred_file:
        cred_file.write(user_creds.to_json())
        logger.debug(f"Credentials saved to {USER_ACCESS_CREDENTIALS_PATH}")

def reauthenticate_and_save():
    logger.info("Starting browser-based reauthentication flow.")
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_PATH, SCOPES
    )
    user_creds = flow.run_local_server(port=0)
    logger.info("User successfully reauthenticated via browser flow.")

    save_user_credentials(user_creds)
    return user_creds

def attempt_credentials_refresh(creds):
    creds.refresh(Request())

def get_credentials():
    """Obtain valid Google API credentials, refreshing or reauthenticating as needed."""
    logger.info("Starting credential retrieval process.")

    if not USER_ACCESS_CREDENTIALS_PATH.exists():
        logger.info(f"Nothing found at {USER_ACCESS_CREDENTIALS_PATH}.")
        return reauthenticate_and_save()

    logger.info(f"Loading credentials from {USER_ACCESS_CREDENTIALS_PATH}")
    user_creds = Credentials.from_authorized_user_file(USER_ACCESS_CREDENTIALS_PATH, SCOPES)

    if user_creds.valid:
        logger.info("Existing credentials are valid. Returning them.")
        return user_creds

    if not user_creds.refresh_token or not user_creds.expired:
        logger.info("Invalid credentials and either lack a refresh token or are not expired.")
        return reauthenticate_and_save()
    
    logger.debug("Credentials are expired and have a refresh token; attempting to refresh.")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(attempt_credentials_refresh, user_creds)
        try:
            _ = future.result(timeout=FETCH_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            logger.warning('Fetch operation timed out during credential refresh. Reauthenticating.')
            return reauthenticate_and_save()
        except RefreshError as e:
            logger.warning(f"Initial refresh attempt failed: {e}. Reauthenticating.")
            return reauthenticate_and_save()
    attempt_credentials_refresh(user_creds)

    save_user_credentials(user_creds)
    return user_creds

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
    logger.info('Fetching current event names, by first fetching credentials...')
    creds = get_credentials()
    logger.info('Credentials obtained. Building calendar service...')
    service = build('calendar', 'v3', credentials=creds)
    calendar_list = service.calendarList().list().execute()
    calendar_ids = [calendar['id'] for calendar in calendar_list.get('items', [])]

    current_events = []
    for calendar_id in calendar_ids:
        current_events.extend(fetch_current_event_names_from_calendar(service, calendar_id))
    logger.info('Fetched event names.')
    return current_events

if __name__ == '__main__':
    logger.info('Running fetch.py directly; fetching and printing current event names.')
    print(fetch_current_event_names())
    logger.info('fetch.py finished running.')