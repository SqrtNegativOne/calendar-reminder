from fastapi import APIRouter, Request, Response
import json
import logging

log = logging.getLogger(__name__)

router = APIRouter()

@router.post("/notifications")
async def receive_notification(request: Request):
    headers = dict(request.headers)
    body = await request.body()
    
    log.info(f"Notification received. Headers: {headers}")
    log.info(f"Body: {body.decode()}")

    event_id = extract_event_id(headers, body.decode())
    if event_id:
        request.app.state.calendar_service.fetch_event_by_id("primary", event_id)

    return Response(status_code=200)

def extract_event_id(headers, body_str):
    # Add real parsing based on your app's needs
    return None
