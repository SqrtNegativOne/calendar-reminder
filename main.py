import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

app = FastAPI()

# ========== GOOGLE AUTH ==========
def get_credentials() -> Credentials:
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


# ========== GOOGLE CALENDAR WATCH ==========
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
    print(f"Started watch:\n{json.dumps(response, indent=2)}")
    return response


# ========== FETCH CALENDAR EVENTS ==========
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
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event.get('summary'))


# ========== NOTIFICATION WEBHOOK ==========
@app.post("/notifications")
async def receive_notification(request: Request):
    headers = dict(request.headers)
    body = await request.body()
    print("🔔 Notification received")
    print("Headers:", json.dumps(headers, indent=2))
    print("Body:", body.decode())

    # React to the notification
    fetch_calendar_events()

    return Response(status_code=200)


# ========== STARTUP: REGISTER WATCH ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP CODE ---
    PUBLIC_WEBHOOK_URL = "https://your-public-url.com/notifications"
    CALENDAR_ID = 'primary'
    start_watch(CALENDAR_ID, PUBLIC_WEBHOOK_URL)

    yield  # The app runs while execution is paused here


app = FastAPI(lifespan=lifespan)

