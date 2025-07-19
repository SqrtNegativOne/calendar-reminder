import tkinter as tk
import logging
logging.basicConfig(level=logging.INFO)

BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
FONT = "fs-sevegment"
DEFAULT_ALPHA = 0.8

WIDTH = 100
HEIGHT = 100
GEOMETRY = f"{WIDTH}x{HEIGHT}+100+100"

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

class Overlay(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        self.logger = logging.getLogger('Overlay')
        self.logger.info('Stopwatch initialised.')

        tk.Tk.__init__(self, *args, **kwargs)
        self.overrideredirect(True) # Rips out the titlebar
        self.attributes('-topmost', True)

        self.config(bg=BACKGROUND_COLOR)
        self.attributes('-alpha', DEFAULT_ALPHA)
        self.minsize(width=WIDTH, height=HEIGHT)
        self.geometry(GEOMETRY)

        self.label: tk.Label = tk.Label(
            self,
            text='Test',
            foreground=TEXT_COLOR,
            font=FONT,
            bg=BACKGROUND_COLOR
        )
        self.label.pack()


def main() -> None:
    Overlay().mainloop()


if __name__ == '__main__':
    main()