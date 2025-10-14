import tkinter as tk
from datetime import datetime
import subprocess
from loguru import logger

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

from fetch import fetch_current_event_names
from config import (
    SCREEN_GEOMETRY, BACKGROUND_COLOR, TEXT_COLOR,
    DEFAULT_ALPHA, HIDING_ALPHA, NO_CURRENT_EVENT_ALPHA, MOUSE_HOVER_ALPHA_CHANGE, MOUSE_CLICK_ALPHA_CHANGE,
    NO_CURRENT_EVENT_MESSAGE, INIT_MESSAGE, REFRESHING_MESSAGE,
    MAX_CHAR_WIDTH_PIXEL_COUNT, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, WINDOWS_TASKBAR_HEIGHT_IN_PIXELS,
    FETCH_INTERVAL_MINUTES,
    LOG_FILE_PATH
)

logger.add(LOG_FILE_PATH)

MINUTE_IN_MILLISECONDS: int = 60 * 1000
FETCH_INTERVAL_MILLISECONDS: int = FETCH_INTERVAL_MINUTES * MINUTE_IN_MILLISECONDS

STOPWATCH_SUBSTRING = 'S;'
STOPWATCH_PATH = r"C:\Users\arkma\Documents\GitHub\StopwatchTK\main.pyw"

def run_stopwatch() -> None:
    try:
        subprocess.Popen(['python', STOPWATCH_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)
        logger.info('Stopwatch launched.')
    except Exception as e:
        logger.error(f'Failed to launch stopwatch: {e}')

def get_current_screen_width_height() -> tuple[int, int]:
    """
    Workaround to get the size of the current screen in a multi-screen setup.
    """
    if SCREEN_GEOMETRY is not None:
        return SCREEN_GEOMETRY
    
    from re import fullmatch
    
    # Find `screen_geometry` by creating a full-screen temporary Tkinter window in current screen
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    screen_geometry = root.winfo_geometry()
    root.destroy()

    match = fullmatch(r"(\d+)x(\d+)\+\d+\+\d+", screen_geometry)
    if not match:
        raise ValueError(f'Received invalid object: {screen_geometry=}')
    
    screen_width, screen_height = map(int, match.groups())
    print(f"Your screen dimensions are: ({screen_width}, {screen_height}).")
    print(f"Input them to the config.py file to speed up GUI initialisation!")
    return screen_width, screen_height

def get_window_geometry(window_width: int, window_height: int) -> str:
    screen_width, screen_height = get_current_screen_width_height()

    window_left = (screen_width - window_width) // 2
    window_top = screen_height - WINDOWS_TASKBAR_HEIGHT_IN_PIXELS - window_height

    return f'{window_width}x{window_height}+{window_left}+{window_top}'

class Overlay(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        logger.info('Overlay window initialised.')

        tk.Tk.__init__(self, *args, **kwargs)
        self.overrideredirect(True) # Rips out the titlebar
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", lambda: logger.info('Overlay kill attempted.')) # Disables Alt-F4

        self.config(bg=BACKGROUND_COLOR)
        self.set_geometry(INIT_MESSAGE)

        self.label_text: tk.StringVar = tk.StringVar(value=INIT_MESSAGE)
        label: tk.Label = tk.Label(
            self,
            textvariable=self.label_text,
            foreground=TEXT_COLOR,
            # font=FONT,
            bg=BACKGROUND_COLOR
        )
        label.pack()

        self.bind_everything()

        self.init_run()
    
    def set_geometry(self, message: str) -> None:
        self.geometry(
            get_window_geometry(
                window_width  = max(MAX_CHAR_WIDTH_PIXEL_COUNT * len(message), MIN_WINDOW_WIDTH),
                window_height = WINDOW_HEIGHT
            )
        )
    
    def bind_everything(self) -> None:
        def Keypress(event):
            if event.char == 'h':
                self.hide()
            elif event.char == 'r':
                self.reset_refresh_timer()
            elif event.char == 'c':
                self.set_geometry(str(self.label_text)) # TODO: fix bug.
        self.bind('<Key>', Keypress)

        self.x = 0
        self.bind('<Button-1>', self.click)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<Enter>', self.hover)
        self.bind('<Leave>', self.mouse_leave)
    
    def click(self, event) -> None:
        self.x = event.x
        self.attributes('-alpha', self.alpha-MOUSE_CLICK_ALPHA_CHANGE)

    def drag(self, event) -> None:
        x = event.x - self.x + self.winfo_x()
        y = self.winfo_y()
        self.geometry(f'+{x}+{y}')
        self.attributes('-alpha', self.alpha-MOUSE_HOVER_ALPHA_CHANGE)

    def mouse_leave(self, event) -> None:
        self.attributes('-alpha', self.alpha)
    
    def hover(self, event) -> None:
        self.attributes('-alpha', self.alpha-MOUSE_HOVER_ALPHA_CHANGE)
    
    def reset_refresh_timer(self) -> None:
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        self.label_text.set(value=REFRESHING_MESSAGE)
        self.update_label_once()
        self.after_id = self.after(FETCH_INTERVAL_MILLISECONDS, self.run)
    
    def update_label_once(self) -> None:
        event_names = fetch_current_event_names()
        if not event_names:
            text = NO_CURRENT_EVENT_MESSAGE
            self.alpha = NO_CURRENT_EVENT_ALPHA
        else:
            if any(STOPWATCH_SUBSTRING in name for name in event_names):
                run_stopwatch()
            text = ' ⋅ '.join(event_names)
            self.alpha = DEFAULT_ALPHA
        self.set_geometry(text)
        self.label_text.set(value=text)
        self.attributes('-alpha', self.alpha)
    
    def init_run(self) -> None:
        self.update_label_once()
        minutes_till_next_interval: int = FETCH_INTERVAL_MINUTES - int(datetime.now().minute) % FETCH_INTERVAL_MINUTES
        logger.info(f'Label updated with current events. Setting next update in {minutes_till_next_interval} minutes.')
        self.after_id = self.after(minutes_till_next_interval * MINUTE_IN_MILLISECONDS, self.run)

    def run(self) -> None:
        self.update_label_once()
        self.after_id = self.after(FETCH_INTERVAL_MILLISECONDS, self.run)
    
    def hide(self) -> None:
        if self.alpha == DEFAULT_ALPHA:
            self.alpha = HIDING_ALPHA
        elif self.alpha == HIDING_ALPHA:
            self.alpha = DEFAULT_ALPHA
        self.attributes('-alpha', self.alpha)


if __name__ == '__main__':
    Overlay().mainloop()