# Timebox Tray Timer

A minimalist, cross-platform **system tray timeboxing tool** for Windows, macOS, and Linux, written in Python using pystray.

- Pick a countdown in number of minutes from the tray icon menu, and the icon will update every minute.
- Beeps when time is up.
- Only allows one instance per machine.

## To add to Task Scheduler

1. `py -3 -m venv .venv`
2. `source v`
3. In Task Scheduler:
    - Trigger: "On workstation unlock of any user" and "At log on of any user".
    - Action: "Start a program" with "Powershell" and arguments "-WindowStyle hidden path\to\run.ps1"