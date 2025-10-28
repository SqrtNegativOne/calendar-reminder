# -------------------------------------------------
# CALENDAR FETCHING / FILE CONFIGURATION
# -------------------------------------------------
from pathlib import Path

BASE_PATH = Path(__file__).parent
SECRETS_PATH = BASE_PATH.parent / 'secrets'

USER_ACCESS_CREDENTIALS_PATH = SECRETS_PATH / 'token.json'
CLIENT_SECRETS_PATH = SECRETS_PATH / 'credentials.json'

LOG_FILE_PATH = BASE_PATH / 'out.log'

# -------------------------------------------------
# CALENDAR FETCHING / TIME CONFIGURATION
# -------------------------------------------------
from datetime import timedelta

# Assumes all tasks in your calendar are mostly ≤ 2 hours long, and searches in MAX_TASK_LENGTH * 2 interval only.
MAX_TASK_LENGTH: timedelta = timedelta(hours=2)
# Maximum calendar items to fetch within the MAX_TASK_LENGTH duration.
MAX_RESULTS_TO_FETCH_PER_CALENDAR: int = 5

# Update the overlay every .. minutes.
FETCH_INTERVAL_MINUTES: int = 15

FETCH_TIMEOUT_SECONDS: int = 8 # Seconds to wait before considering the fetch operation as timed out.

# -------------------------------------------------
# REMINDER APP / GUI CONFIGURATION
# -------------------------------------------------

# Size of your screen; (width, height) in pixels.
# This is used to position the overlay window.
# If you don't know it, run `screen_geometry.py` in the utils folder.
# Note: windll DPI awareness multiplies pixel sizes by 1.25. So (1536, 960)→(1960, 1200), 48→60
SCREEN_GEOMETRY: tuple[int, int] = (1920, 1200)
WINDOWS_TASKBAR_HEIGHT_IN_PIXELS = 55 # for my custom windows taskbar. default is 60

FONT_FAMILY: str = "Segoe UI"
FONT_SIZE: int = 9

MIN_WINDOW_WIDTH: int = 50 # Window width won't go lower than this.
WINDOW_HEIGHT: int = 26

BACKGROUND_COLOR: str =   '#181818'
TEXT_COLOR:       str =   "#FFFFFF"

NON_EVENT_ALPHA:          float =       0.20 # When refreshing, or no current event.
DEFAULT_ALPHA:            float =       0.70
HIDING_ALPHA:             float =       0.20
MOUSE_HOVER_ALPHA_CHANGE: float =       0.10
MOUSE_CLICK_ALPHA_CHANGE: float =       0.15

assert 0.05 <= MOUSE_HOVER_ALPHA_CHANGE < MOUSE_CLICK_ALPHA_CHANGE < HIDING_ALPHA <= NON_EVENT_ALPHA < DEFAULT_ALPHA < 1.0

NO_CURRENT_EVENT_MESSAGE: str = '[no current event]'
REFRESHING_MESSAGE: str = '[refreshing]'
TIMEOUT_RETRY_MESSAGE: str = '[fetch timed out. retrying]'
FREQUENT_TIMEOUT_MESSAGE: str = '[frequent timeouts detected. check wifi and logs]'

# -------------------------------------------------
# REMINDER APP / EXTERNAL APPS CONFIGURATION
# -------------------------------------------------
from app_config import py, exe, App

APP_CODE_PREFIX: str = ';'
APPS: dict[str, App] = {
    'A': App(exe(r"C:\Users\arkma\AppData\Local\Programs\Anki\anki.exe")),
    # bcdefghijklmn
    'O': App(exe(r"C:\Users\arkma\AppData\Local\Programs\obsidian\Obsidian.exe")),
    # pqr
    'S': App(py(r"C:\Users\arkma\Documents\GitHub\StopwatchTK\main.pyw", interpreter=r"C:\Users\arkma\Documents\GitHub\StopwatchTK\.venv\Scripts\pythonw.exe")),
    # tuvwxyz
}


if __name__ == '__main__':
    print('The `config.py` file isn\'t meant to be run directly. Run the `reminder.py` file instead.')