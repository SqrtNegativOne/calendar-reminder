# -------------------------------------------------
# FILES
# -------------------------------------------------
from pathlib import Path

BASE_PATH = Path(__file__).parent
SECRETS_PATH = BASE_PATH.parent / 'secrets'

CREDS_PATH = SECRETS_PATH / 'token.json'
CREDENTIALS_PATH = SECRETS_PATH / 'credentials.json'

LOG_FILE_PATH = BASE_PATH / 'out.log'

# -------------------------------------------------
# FETCH CONFIGURATION
# -------------------------------------------------
from datetime import timedelta

# Assumes all tasks in your calendar are ≤ 2 hours long, and searches in MAX_TASK_LENGTH * 2 interval only.
MAX_TASK_LENGTH: timedelta = timedelta(hours=2)
# Maximum calendar items to fetch within the MAX_TASK_LENGTH duration.
MAX_RESULTS_TO_FETCH_PER_CALENDAR: int = 5

# Update the overlay every .. minutes.
FETCH_INTERVAL_MINUTES: int = 15

FETCH_TIMEOUT_SECONDS: int = 8 # Seconds to wait before considering the fetch operation as timed out.

# -------------------------------------------------
# REMINDER APP CONFIGURATION
# -------------------------------------------------

# Size of your screen; (width, height) in pixels.
# This is used to position the overlay window.
# Use `None` to force the application to calculate it upon initialisation.
# Note: windll DPI awareness multiplies pixel sizes by 1.25. So (1536, 960)→(1960, 1200), 48→60
SCREEN_GEOMETRY: tuple[int, int] | None = (1920, 1200)
WINDOWS_TASKBAR_HEIGHT_IN_PIXELS = 52 # for my custom windows taskbar. default is 60

MAX_CHAR_WIDTH_PIXEL_COUNT: int = 10 # Maximum width of a character in the font used, in pixels. Used to calculate window width.
MIN_WINDOW_WIDTH: int = 50 # Window width won't go lower than this.
WINDOW_HEIGHT: int = 28

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


if __name__ == '__main__':
    print('The `config.py` file isn\'t meant to be run directly. Run the `reminder.py` file instead.')