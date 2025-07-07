import os
from pathlib import Path

SECRETS_PATH = Path(__file__).parent.parent
TOKEN_PATH = SECRETS_PATH / 'token.json'
CREDENTIALS_PATH = SECRETS_PATH / 'credentials.json'

SCOPES = ['https://www.googleapis.com/auth/calendar']
PORT = int(os.getenv("PORT", 8000))
LOCAL_DEV = os.getenv("ENV", "dev") == "dev"


BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
FONT = "fs-sevegment"
DEFAULT_ALPHA = 0.8

WIDTH = 10
HEIGHT = 100
GEOMETRY = f"{WIDTH}x{HEIGHT}+0+800"