Calendar reminders to keep you focused.
- Polls your calendar every 15 minutes to find what the current task is and displays it consistently at the bottom of your screen.
- If the task contains a special code, it launches an associated application (e.g., Anki, Obsidian, Stopwatch) automatically, kind of "forcing" you to switch from the current context to the desired one.
- The program should automatically authenticate with Google Calendar by opening a browser window to connect to your calendar the first time it is run, but I have only tested this on my own machine.

To make any changes, just change the variables in `config.py`.

To use:
1. Clone repository.
2. Download `uv` using `pip install uv` or more preferably `curl -LsSf https://astral.sh/uv/install.sh | sh`.
3. Run `uv sync` in the project directory to install dependencies.
4. If you are running on Windows, create a shortcut for `remind-init.ps1` in your startup folder to have it run on login. If you're on MacOS or Linux, set up a cron job or equivalent to run `remind-init.sh` on login.