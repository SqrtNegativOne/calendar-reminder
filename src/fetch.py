from datetime import datetime, timezone, time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
from pathlib import Path

SECRETS_PATH = Path(__file__).parent.parent
TOKEN_PATH = SECRETS_PATH / 'token.json'
CREDENTIALS_PATH = SECRETS_PATH / 'credentials.json'

SCOPES = ['https://www.googleapis.com/auth/calendar']
LOCAL_DEV = os.getenv("ENV", "dev") == "dev"

MAX_RESULTS_TO_FETCH = 12  # Maximum number of calendar items to fetch

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TODAY = datetime.now(timezone.utc).date()
TODAY_START = datetime.combine(TODAY, time.min, tzinfo=timezone.utc).isoformat()
TODAY_END = datetime.combine(TODAY, time.max, tzinfo=timezone.utc).isoformat()

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

def fetch_num_calendar_items_for_one_calendar(service, calendar_id: str) -> int:
    """Fetch the number of calendar items for a single calendar."""
    try:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=TODAY_START,
                timeMax=TODAY_END,
                maxResults=MAX_RESULTS_TO_FETCH,  # Don't fetch more than we need
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get('items', None)
        return len(events) if events else 0
    except HttpError as error:
        logging.error(f"Error fetching calendar items: {error}")
        return 0

def adequate_google_cal_tasks_scheduled():
    service = build('calendar', 'v3', credentials=get_credentials())
    calendar_list = service.calendarList().list().execute()
    calendar_ids = [calendar['id'] for calendar in calendar_list.get('items', [])]

    items_count = 0
    for calendar_id in calendar_ids:
        items_count += fetch_num_calendar_items_for_one_calendar(service, calendar_id)