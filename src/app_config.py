import subprocess
from pathlib import Path
from typing import Callable
# from loguru import logger; Don't log here, just raise errors. Logging will occur in the caller.


class App:
    def __init__(self, launch_callable: Callable):
        self.launch_callable = launch_callable
        self.already_running = False

    def launch(self):
        if self.already_running: return
        self.already_running = True
        self.launch_callable()


def py(py_path: str, interpreter: str | None = None) -> Callable:
    if not Path(py_path).is_file():
        raise ValueError(f'Python script path does not point to a valid file: {py_path}')
    if not (py_path.lower().endswith('.pyw') or py_path.lower().endswith('.py')):
        raise ValueError(f'Python script path must end with .py or .pyw: {py_path}')
    if isinstance(interpreter, str):
        if not Path(interpreter).is_file():
            raise ValueError(f'Interpreter path does not point to a valid file: {interpreter}')
        if not interpreter.lower().endswith('.exe'):
            raise ValueError(f'Interpreter path must point to an .exe file: {interpreter}')
    else:
        if py_path.lower().endswith('.pyw'):
            interpreter = 'pythonw'
        else:
            interpreter = 'python'
    
    return lambda: subprocess.Popen(
        [interpreter, py_path],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    )

def exe(exe_path: str) -> Callable:
    if not Path(exe_path).is_file():
        raise ValueError(f'Executable path does not point to a valid file: {exe_path}')
    if not exe_path.lower().endswith('.exe'):
        raise ValueError(f'Path does not point to an .exe file: {exe_path}')
    
    return lambda: subprocess.Popen([exe_path], shell=True)