import tkinter as tk

def get_current_screen_width_height() -> tuple[int, int]:
    """
    Workaround to get the size of the current screen in a multi-screen setup.
    """
    
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

print(get_current_screen_width_height())