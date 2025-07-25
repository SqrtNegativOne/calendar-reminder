# -------------------------------------------------
# FETCH CONFIGURATION
# -------------------------------------------------

from datetime import timedelta
# Assumes all tasks in your calendar are ≤ 2 hours long, and searches in MAX_TASK_LENGTH * 2 interval only.
MAX_TASK_LENGTH = timedelta(hours=2)
# Maximum calendar items to fetch within the MAX_TASK_LENGTH duration.
MAX_RESULTS_TO_FETCH_PER_CALENDAR = 5

# Update the overlay every .. minutes.
FETCH_INTERVAL_MINUTES: int = 15

# -------------------------------------------------
# REMINDER APP CONFIGURATION
# -------------------------------------------------

# Size of your screen; (width, height) in pixels.
# This is used to position the overlay window correctly.
# Use `None` to force the application to calculate it upon initialisation.
# Note: windll DPI awareness multiplies pixel sizes by 1.25. So (1536, 960)→(1960, 1200), 48→60
SCREEN_GEOMETRY: tuple[int, int] | None = (1920, 1200)
WINDOWS_TASKBAR_HEIGHT_IN_PIXELS = 52 # for my custom windows taskbar. default is 60

MAX_CHAR_WIDTH_PIXEL_COUNT: int = 10 # Maximum width of a character in the font used, in pixels. Used to calculate window width.
# WINDOW_WIDTH: int = 300
WINDOW_HEIGHT: int = 28

BACKGROUND_COLOR: str = '#181818'
TEXT_COLOR: str = "#FFFFFF"

NO_CURRENT_EVENT_ALPHA:   float =       0.2
DEFAULT_ALPHA:            float =       0.7
HIDING_ALPHA:             float =       0.2
MOUSE_HOVER_ALPHA_CHANGE: float =       0.1
MOUSE_CLICK_ALPHA_CHANGE: float =       0.15

INIT_MESSAGE: str = '~initialized~' # Only shown for a couple of milliseconds probably.
NO_CURRENT_EVENT_MESSAGE: str = '~no current event~'



if __name__ == '__main__':
    print('The `config.py` file isn\'t meant to be run directly. Run the `reminder.py` file instead.')