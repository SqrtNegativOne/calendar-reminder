import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
from loguru import logger # same as the logger in fetch.py, so logs go to the same file
import concurrent.futures
from dotenv import load_dotenv
load_dotenv()


from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

from fetch import fetch_current_event_names

from config import (
    SCREEN_GEOMETRY, BACKGROUND_COLOR, TEXT_COLOR,
    FONT_FAMILY, FONT_SIZE,
    DEFAULT_ALPHA, HIDING_ALPHA, NON_EVENT_ALPHA, MOUSE_HOVER_ALPHA_CHANGE, MOUSE_CLICK_ALPHA_CHANGE,
    NO_CURRENT_EVENT_MESSAGE, REFRESHING_MESSAGE, TIMEOUT_RETRY_MESSAGE, FREQUENT_TIMEOUT_MESSAGE,
    MIN_WINDOW_WIDTH, WINDOW_HEIGHT, WINDOWS_TASKBAR_HEIGHT_IN_PIXELS,
    FETCH_INTERVAL_MINUTES, FETCH_TIMEOUT_SECONDS,
    APPS, APP_CODE_PREFIX
)

TEXT_PADDING_IN_PIXELS: int = 16
MAX_MESSAGE_LENGTH: int = 80

SECOND_IN_MILLISECONDS: int = 1000
FETCH_INTERVAL_MILLISECONDS: int = FETCH_INTERVAL_MINUTES * SECOND_IN_MILLISECONDS * 60


class Overlay(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        logger.info('Setting up overlay window...')

        self.overrideredirect(True) # Rips out the titlebar
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", lambda: logger.info('Overlay kill attempted.'))

        self.config(bg=BACKGROUND_COLOR)
        
        self.font: tkfont.Font = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE, weight='normal') # Needed for measuring text width.
        self._init_geometry()
        self.update_idletasks()
        self._label_text: tk.StringVar = tk.StringVar(value=REFRESHING_MESSAGE)
        label: tk.Label = tk.Label(
            self,
            textvariable=self._label_text,
            foreground=TEXT_COLOR,
            font=self.font,
            bg=BACKGROUND_COLOR
        )
        label.pack()

        self._idle_alpha: float = DEFAULT_ALPHA
        self.attributes('-alpha', self._idle_alpha)
        
        self.timeout_happened_before: bool = False

        self._bind_everything()

        self.run()
    
    def _init_geometry(self) -> None:
        screen_width, screen_height = SCREEN_GEOMETRY

        window_width = max(self.font.measure(REFRESHING_MESSAGE) + TEXT_PADDING_IN_PIXELS, MIN_WINDOW_WIDTH)
        window_height = WINDOW_HEIGHT

        window_left = (screen_width - window_width) // 2
        window_top = screen_height - WINDOWS_TASKBAR_HEIGHT_IN_PIXELS - window_height

        geometry = f'{window_width}x{window_height}+{window_left}+{window_top}'
        logger.info(f'Initial geometry: {geometry}')
        self.geometry(geometry)
    
    def center_horizontally(self) -> None:
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        self.geometry(f'{self.winfo_width()}x{self.winfo_height()}+{x}+{self.winfo_y()}')
        self.overrideredirect(True)

    def change_width(self, message: str) -> None:
        logger.info(f'Geometry: {self.geometry()}')
        width = max(self.font.measure(message) + TEXT_PADDING_IN_PIXELS, MIN_WINDOW_WIDTH)
        x = self.winfo_x()
        if x + width > self.winfo_screenwidth():
            x = self.winfo_screenwidth() - width
        elif x < 0:
            x = 0
        self.geometry(f"{width}x{self.winfo_height()}+{x}+{self.winfo_y()}")
        self.overrideredirect(True)
    
    def _bind_everything(self) -> None:
        def Keypress(event):
            key = event.char
            logger.info(f'Key pressed: {key}')
            if key == 'h':
                self.toggle_hide()
            elif key == 'r':
                self.change_label_text_to(REFRESHING_MESSAGE)
                self.run()
            elif key == 'c':
                self.center_horizontally()
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
        self.attributes('-alpha', self._idle_alpha-MOUSE_CLICK_ALPHA_CHANGE) # We are clicking when we are dragging.

    def mouse_leave(self, event) -> None:
        self.attributes('-alpha', self._idle_alpha)
    
    def hover(self, event) -> None:
        self.attributes('-alpha', self._idle_alpha-MOUSE_HOVER_ALPHA_CHANGE)

    def change_label_text_to(self, new_text: str) -> None:
        if len(new_text) > MAX_MESSAGE_LENGTH:
            logger.warning(f'Label text exceeds max length ({MAX_MESSAGE_LENGTH}): {new_text}')
            new_text = new_text[:MAX_MESSAGE_LENGTH] + '...'
        self._label_text.set(value=new_text)
        self.change_width(new_text)
        logger.info(f'Label text changed to: {new_text}')

    def change_idle_alpha_to(self, new_idle_alpha: float) -> None:
        self._idle_alpha = new_idle_alpha
        self.attributes('-alpha', new_idle_alpha)
    
    @staticmethod
    def run_apps_from_event_names(event_names: list[str]) -> None:
        for i, name in enumerate(event_names):
            for app_code in APPS.keys():
                substring = APP_CODE_PREFIX + app_code
                if not substring in name:
                    APPS[app_code].already_running = False # Reset for next time.
                    continue
                
                event_names[i] = name.replace(substring, '').strip()
                try:
                    APPS[app_code].launch() # Launches the app.
                except Exception as e:
                    logger.error(f'Error launching app for code {app_code}: {e}')

    def update_label_with_events_once(self) -> None:
        # Try not to have logging here, have it only in the functions called from here.

        # self.change_label_text_to(REFRESHING_MESSAGE)
        # self.change_idle_alpha_to(NON_EVENT_ALPHA)
        # Don't change alpha while refreshing; it may be hidden + distracting to change it when it isn't.

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_current_event_names)
            try:
                event_names: list[str] = future.result(timeout=FETCH_TIMEOUT_SECONDS)
            except concurrent.futures.TimeoutError:
                if self.timeout_happened_before:
                    self.change_label_text_to(FREQUENT_TIMEOUT_MESSAGE)
                    self.change_idle_alpha_to(NON_EVENT_ALPHA)
                    return
                self.timeout_happened_before = True
                self.change_label_text_to(TIMEOUT_RETRY_MESSAGE)
                return
            except Exception as e:
                self.change_label_text_to('⚠' + str(e) + '⚠')
                self.change_idle_alpha_to(DEFAULT_ALPHA)
                return

        if not event_names:
            self.change_label_text_to(NO_CURRENT_EVENT_MESSAGE)
            self.change_idle_alpha_to(NON_EVENT_ALPHA)
            return

        self.run_apps_from_event_names(event_names)
        self.change_label_text_to(' ⋅ '.join(event_names))
        self.change_idle_alpha_to(DEFAULT_ALPHA)

    def run(self) -> None:
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        self.update_label_with_events_once()
        now = datetime.now()
        seconds_till_next_interval: int = \
            (FETCH_INTERVAL_MINUTES - int(now.minute) % FETCH_INTERVAL_MINUTES) * 60 - now.second - FETCH_TIMEOUT_SECONDS
        logger.info(f'Next update in {seconds_till_next_interval} second(s) (at least {seconds_till_next_interval // 60} minute(s)).')
        self.after_id = self.after(seconds_till_next_interval * SECOND_IN_MILLISECONDS, self.run)

    def toggle_hide(self) -> None:
        if self._idle_alpha == DEFAULT_ALPHA:
            self.change_idle_alpha_to(HIDING_ALPHA)
        else:
            self.change_idle_alpha_to(DEFAULT_ALPHA)


if __name__ == '__main__':
    Overlay().mainloop()