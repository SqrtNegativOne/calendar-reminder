import os
import json
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/calendar']

BASE = Path(__file__).resolve()
TOKEN_PATH = BASE.parent / 'token.json'
CREDENTIALS_PATH = BASE.parent / 'credentials.json'

def get_credentials():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds


# ===================== GOOGLE CALENDAR WATCH =====================
def start_watch(calendar_id: str, webhook_url: str):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    channel_id = f"calendar-watch-{datetime.utcnow().timestamp()}"
    body = {
        'id': channel_id,
        'type': 'web_hook',
        'address': webhook_url,
    }

    response = service.events().watch(calendarId=calendar_id, body=body).execute()
    print(f"✅ Started watch:\n{json.dumps(response, indent=2)}")
    return response


# ===================== FETCH CALENDAR EVENTS =====================
def fetch_calendar_events():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        print('No upcoming events.')
    else:
        print('Upcoming events:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {start}: {event.get('summary')}")


# ===================== FASTAPI APP =====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    PUBLIC_WEBHOOK_URL = "https://your-public-url.com/notifications"  # <- Replace with your public HTTPS URL
    CALENDAR_ID = 'primary'  # Change if you want a different calendar
    start_watch(CALENDAR_ID, PUBLIC_WEBHOOK_URL)

    yield

    # SHUTDOWN (optional): cancel watches, cleanup resources here if needed


app = FastAPI(lifespan=lifespan)


@app.post("/notifications")
async def receive_notification(request: Request):
    headers = dict(request.headers)
    body = await request.body()

    print("🔔 Notification received:")
    print("Headers:", json.dumps(headers, indent=2))
    print("Body:", body.decode())

    # Example: fetch latest events
    fetch_calendar_events()

    return Response(status_code=200)