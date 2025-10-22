import tkinter as tk
from datetime import datetime
import subprocess
from loguru import logger
import concurrent.futures
from os import system, getenv
from dotenv import load_dotenv
load_dotenv()

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

from fetch import fetch_current_event_names
from config import (
    SCREEN_GEOMETRY, BACKGROUND_COLOR, TEXT_COLOR,
    DEFAULT_ALPHA, HIDING_ALPHA, NO_CURRENT_EVENT_ALPHA, MOUSE_HOVER_ALPHA_CHANGE, MOUSE_CLICK_ALPHA_CHANGE,
    NO_CURRENT_EVENT_MESSAGE, INIT_MESSAGE, REFRESHING_MESSAGE, TIMEOUT_MESSAGE,
    MAX_CHAR_WIDTH_PIXEL_COUNT, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, WINDOWS_TASKBAR_HEIGHT_IN_PIXELS,
    FETCH_INTERVAL_MINUTES, FETCH_TIMEOUT_SECONDS,
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
        self._set_geometry(INIT_MESSAGE)

        self._label_text: tk.StringVar = tk.StringVar(value=INIT_MESSAGE)
        label: tk.Label = tk.Label(
            self,
            textvariable=self._label_text,
            foreground=TEXT_COLOR,
            # font=FONT,
            bg=BACKGROUND_COLOR
        )
        label.pack()

        self._bind_everything()

        self.run()
    
    def _set_geometry(self, message: str) -> None:
        self.geometry(
            get_window_geometry(
                window_width  = max(MAX_CHAR_WIDTH_PIXEL_COUNT * len(message), MIN_WINDOW_WIDTH),
                window_height = WINDOW_HEIGHT
            )
        )
    
    def _bind_everything(self) -> None:
        def Keypress(event):
            if event.char == 'h':
                self.toggle_hide()
            elif event.char == 'r':
                self.run()
        self.bind('<Key>', Keypress)

        self.x = 0
        self.bind('<Button-1>', self.click)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<Enter>', self.hover)
        self.bind('<Leave>', self.mouse_leave)
    
    def click(self, event) -> None:
        self.x = event.x
        self.attributes('-alpha', self._idle_alpha-MOUSE_CLICK_ALPHA_CHANGE)
    
    def release(self, event) -> None:
        self.attributes('-alpha', self._idle_alpha)

    def drag(self, event) -> None:
        x = event.x - self.x + self.winfo_x()
        if x < 0:
            x = 0
        elif x > self.winfo_screenwidth() - self.winfo_width():
            x = self.winfo_screenwidth() - self.winfo_width()
        y = self.winfo_y()
        self.geometry(f'+{x}+{y}')
        #self.attributes('-alpha', self._idle_alpha-MOUSE_HOVER_ALPHA_CHANGE) # We technically don't click when dragging.
        self.attributes('-alpha', self._idle_alpha-MOUSE_CLICK_ALPHA_CHANGE) # or do we? idk

    def mouse_leave(self, event) -> None:
        self.attributes('-alpha', self._idle_alpha)
    
    def hover(self, event) -> None:
        self.attributes('-alpha', self._idle_alpha-MOUSE_HOVER_ALPHA_CHANGE)
    
    def change_label_text_to(self, new_text: str) -> None:
        self._set_geometry(new_text)
        self._label_text.set(value=new_text)
    
    def change_idle_alpha_to(self, new_idle_alpha: float) -> None:
        self._idle_alpha = new_idle_alpha
        self.attributes('-alpha', new_idle_alpha)

    def update_label_with_events_once(self) -> None:
        self.change_label_text_to(REFRESHING_MESSAGE)
        logger.info('Set label to REFRESHING_MESSAGE.')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_current_event_names)
            try:
                event_names: list[str] = future.result(timeout=FETCH_TIMEOUT_SECONDS)
            except concurrent.futures.TimeoutError:
                logger.warning('Fetch current event names timed out.')
                event_names = [TIMEOUT_MESSAGE]

        if not event_names:
            logger.info('No current events found after fetch.')
            self.change_label_text_to(NO_CURRENT_EVENT_MESSAGE)
            self.change_idle_alpha_to(NO_CURRENT_EVENT_ALPHA)
            return

        if any(STOPWATCH_SUBSTRING in name for name in event_names):
            run_stopwatch()
        self.change_label_text_to(' ⋅ '.join(event_names))
        self.change_idle_alpha_to(DEFAULT_ALPHA)
        logger.info(f'Updated label with events: {event_names}')

    def run(self) -> None:
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        self.update_label_with_events_once()
        minutes_till_next_interval: int = FETCH_INTERVAL_MINUTES - int(datetime.now().minute) % FETCH_INTERVAL_MINUTES
        logger.info(f'Next update in {minutes_till_next_interval} minute(s).')
        self.after_id = self.after(minutes_till_next_interval * MINUTE_IN_MILLISECONDS, self.run)

    def toggle_hide(self) -> None:
        if self._idle_alpha == DEFAULT_ALPHA:
            self.change_idle_alpha_to(HIDING_ALPHA)
        else:
            self.change_idle_alpha_to(DEFAULT_ALPHA)


if __name__ == '__main__':
    Overlay().mainloop()