#!/bin/sh
scriptPath=$(cd "$(dirname "$0")" && pwd)
cd "$scriptPath" || exit 1

# Run in background, survive logout
nohup "$scriptPath/.venv/bin/python" "$scriptPath/src/reminder.pyw" >/dev/null 2>&1 &
