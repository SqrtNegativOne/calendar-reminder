Calendar reminders to keep you focused.
- Polls your calendar every 15 minutes to find what the current task is and displays it consistently at the bottom of your screen.
- If the task contains a special code, it launches an associated application (e.g., Anki, Obsidian, Stopwatch) automatically, kind of "forcing" you to switch from the current context to the desired one.
- The program should automatically authenticate with Google Calendar by opening a browser window to connect to your calendar the first time it is run, but I have only tested this on my own machine.

To make any changes, just change the variables in `config.py`.

# Setup Instructions
## Installation
1. Clone repository.
2. Download `uv` using `pip install uv` or more preferably `curl -LsSf https://astral.sh/uv/install.sh | sh`.
3. Run `uv sync` in the project directory to install dependencies.
4. If you are running on Windows, create a shortcut for `remind-init.ps1` in your startup folder to have it run on login. If you're on MacOS or Linux, set up a cron job or equivalent to run `remind-init.sh` on login.

## Google Calendar API Setup
Unfortunately Google does not allow me to automate this process unless I go through a lengthy verification and publishing process, so you will need to set up your own OAuth 2.0 credentials to use the Google Calendar API.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the Google Calendar API for your project.
4. Create credentials (OAuth 2.0 Client IDs) for your application.
5. Download the `credentials.json` file and place it in the `secrets` directory of the project, just outside of the `src` directory. (You may need to create this directory if it does not exist.)
6. The first time you run the program, it will open a browser window to authenticate with your Google account and request access to your calendar. After successful authentication, it will save the access and refresh tokens in `token.json` in the `secrets` directory for future use.

⚠️ Google Calendar API has this weird bug where reauthentication is not possible in the browser in which you are already logged in, and would show an unhelpful and generic "Something went wrong" error. This isn't my fault Google is just garbage