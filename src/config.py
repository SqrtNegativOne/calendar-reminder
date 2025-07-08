import os
from pathlib import Path

SECRETS_PATH = Path(__file__).parent.parent
TOKEN_PATH = SECRETS_PATH / 'token.json'
CREDENTIALS_PATH = SECRETS_PATH / 'credentials.json'

SCOPES = ['https://www.googleapis.com/auth/calendar']
LOCAL_DEV = os.getenv("ENV", "dev") == "dev"

MAX_RESULTS_TO_FETCH = 12  # Maximum number of calendar items to fetch


BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
FONT = "fs-sevegment"
DEFAULT_ALPHA = 0.8

WIDTH = 100
HEIGHT = 10
GEOMETRY = f"{WIDTH}x{HEIGHT}+1000+1000"