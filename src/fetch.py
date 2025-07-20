from datetime import datetime, timezone, time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
LOCAL_DEV = os.getenv("ENV", "dev") == "dev"

MAX_RESULTS_TO_FETCH_PER_CALENDAR = 3  # Maximum number of calendar items to fetch

from pathlib import Path
SECRETS_PATH = Path(__file__).parent.parent / 'secrets'
TOKEN_PATH = SECRETS_PATH / 'token.json'
CREDENTIALS_PATH = SECRETS_PATH / 'credentials.json'

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_credentials():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_current_event_names_from_calendar(service, calendar_id) -> list[str]:
    now = datetime.now(timezone.utc)
    now_iso_format = now.isoformat()
    try:
        events_response = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now_iso_format,
                timeMax=now_iso_format,
                maxResults=MAX_RESULTS_TO_FETCH_PER_CALENDAR,  # Don't fetch more than we need
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError as error:
        logging.error(f"Error fetching calendar items: {error}")
        return []
    
    event_objects = events_response.get('items', None)
    if event_objects is None:
        logging.error(f"The returned dictionary did not have an items attribute despite no HttpErrors. Shouldn't be possible.")
        return []
    
    current_event_names = []
    for event in event_objects:
        start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
        if start <= now < end:
            current_event_names.append(event['summary'])
    
    return current_event_names

def fetch_current_event_names() -> list[str]:
    service = build('calendar', 'v3', credentials=get_credentials())
    calendar_list = service.calendarList().list().execute()
    calendar_ids = [calendar['id'] for calendar in calendar_list.get('items', [])]

    current_events = []
    for calendar_id in calendar_ids:
        current_events.extend(fetch_current_event_names_from_calendar(service, calendar_id))
    return current_events

if __name__ == '__main__': # Not really meant to be run directly but if it is...
    print(fetch_current_event_names())