# -------------------------------------------------
# FETCH CONFIGURATION
# -------------------------------------------------

from datetime import timedelta
# Assumes all tasks in your calendar are ≤ 2 hours long, and searches in MAX_TASK_LENGTH * 2 interval only.
MAX_TASK_LENGTH = timedelta(hours=2)
# Maximum calendar items to fetch within the MAX_TASK_LENGTH duration.
MAX_RESULTS_TO_FETCH_PER_CALENDAR = 5

# -------------------------------------------------
# REMINDER APP CONFIGURATION
# -------------------------------------------------

# Size of your screen; (width, height) in pixels.
# This is used to position the overlay window correctly.
# Use `None` to force the application to calculate it upon initialisation.
SCREEN_GEOMETRY: tuple[int, int] | None = (1920, 1200) # In reality it's (1536, 960) but windll DPI awareness messes stuff up...
WINDOWS_TASKBAR_HEIGHT_IN_PIXELS = 58 # In reality it's 48 but windll DPI awareness messes stuff up...

WINDOW_WIDTH: int = 300
WINDOW_HEIGHT: int = 30

BACKGROUND_COLOR: str = "#000000"
TEXT_COLOR: str = "#FFFFFF"
FONT: str = "fs-sevegment"
DEFAULT_ALPHA: float = 0.8



if __name__ == '__main__':
    print('This program isn\'t meant to be run directly. Run the `reminder.py` file instead.')