from googleapiclient.discovery import build
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self, credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
        self.channel = None

    def start_watch(self, calendar_id: str, webhook_url: str):
        channel_id = f"calendar-watch-{datetime.now(timezone.utc).timestamp()}"
        body = {
            'id': channel_id,
            'type': 'web_hook',
            'address': webhook_url,
        }
        response = self.service.events().watch(calendarId=calendar_id, body=body).execute()
        self.channel = response
        logger.info(f"Started watch: {json.dumps(response, indent=2)}")
        return response

    def fetch_event_by_id(self, calendar_id: str, event_id: str):
        event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        logger.info(f"Fetched event: {json.dumps(event, indent=2)}")
        return event

    def stop_watch(self):
        if not self.channel:
            return
        self.service.channels().stop(body={
            "id": self.channel.get("id"),
            "resourceId": self.channel.get("resourceId")
        }).execute()
        logger.info("Stopped calendar watch.")
