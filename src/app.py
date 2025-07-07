from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from auth import load_credentials
from calendar_service import CalendarService
from notifications import router
from tunnel_service import start_localtunnel
from config import LOCAL_DEV, PORT

log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting FastAPI app.")

    creds = load_credentials()
    app.state.calendar_service = CalendarService(creds)

    if LOCAL_DEV:
        public_url = await start_localtunnel(PORT)
    else:
        public_url = "https://your-production-url.com"  # Replace with real production URL

    app.state.calendar_service.start_watch("primary", f"{public_url}/notifications")

    yield

    app.state.calendar_service.stop_watch()
    log.info("Shutdown complete.")

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app
