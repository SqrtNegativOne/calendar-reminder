import tkinter as tk
import logging
logging.basicConfig(level=logging.INFO)

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

FIFTEEN_MINTUTES_IN_SECONDS = 60 * 15
FETCH_INTERVAL_MILLISECONDS = FIFTEEN_MINTUTES_IN_SECONDS * 1000

from fetch import fetch_current_event_names
from config import (
    SCREEN_GEOMETRY, BACKGROUND_COLOR, TEXT_COLOR, FONT, DEFAULT_ALPHA, HIDING_ALPHA,
    DEFAULT_MESSAGE, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOWS_TASKBAR_HEIGHT_IN_PIXELS
)

def loadfont(fontpath, private=True, enumerable=False):
    from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
    FR_PRIVATE  = 0x10
    FR_NOT_ENUM = 0x20
    '''
    Makes fonts located in file `fontpath` available to the font system.

    `private`     if True, other processes cannot see this font, and this
                  font will be unloaded when the process dies
    `enumerable`  if True, this font will appear when enumerating fonts

    See https://msdn.microsoft.com/en-us/library/dd183327(VS.85).aspx

    '''
    # This function was taken from
    # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
    if isinstance(fontpath, bytes):
        pathbuf = create_string_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExA
    elif isinstance(fontpath, str):
        pathbuf = create_unicode_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExW
    else:
        raise TypeError('fontpath must be of type str or unicode')

    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
    return bool(numFontsAdded)
#loadfont(r"")

def get_current_screen_width_height() -> tuple[int, int]:
    """
    Workaround to get the size of the current screen in a multi-screen setup.
    """
    if SCREEN_GEOMETRY is not None:
        return SCREEN_GEOMETRY
    
    import re
    
    # Find `screen_geometry` by creating a full-screen temporary Tkinter window in current screen
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    screen_geometry = root.winfo_geometry()
    root.destroy()

    match = re.fullmatch(r"(\d+)x(\d+)\+\d+\+\d+", screen_geometry)
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
        self.logger = logging.getLogger('Overlay')
        self.logger.info('Stopwatch initialised.')

        tk.Tk.__init__(self, *args, **kwargs)
        self.overrideredirect(True) # Rips out the titlebar
        self.attributes('-topmost', True)

        self.config(bg=BACKGROUND_COLOR)
        self.attributes('-alpha', DEFAULT_ALPHA)
        self.geometry(get_window_geometry(
            window_width  = WINDOW_WIDTH,
            window_height = WINDOW_HEIGHT
        ))

        self.label_text: tk.StringVar = tk.StringVar(value=DEFAULT_MESSAGE)
        label: tk.Label = tk.Label(
            self,
            textvariable=self.label_text,
            foreground=TEXT_COLOR,
            font=FONT,
            bg=BACKGROUND_COLOR
        )
        label.pack()

        self.bind_everything()

        self.run()
    
    def bind_everything(self) -> None:
        def Keypress(event):
            if event.char == 'h':
                self.hide()
            elif event.char == 'r':
                self.update_label_once()
        self.bind('<Key>', Keypress)
    
    def update_label_once(self) -> None:
        event_names = fetch_current_event_names()
        if not event_names:
            text = 'No current event.'
        else:
            text = ' ⋅ '.join(event_names)
        self.label_text.set(value=text)

    def run(self) -> None:
        self.update_label_once()
        self.after(FETCH_INTERVAL_MILLISECONDS, self.run)
    
    def hide(self) -> None:
        if self.alpha == DEFAULT_ALPHA:
            self.alpha = HIDING_ALPHA
        elif self.alpha == HIDING_ALPHA:
            self.alpha = DEFAULT_ALPHA
        self.attributes('-alpha', self.alpha)


if __name__ == '__main__':
    Overlay().mainloop()