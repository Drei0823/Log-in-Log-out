# Log-in-Log-out

A simple Python-based Log-In / Log-Out system using SQLite for session tracking and history storage.

## Features

- Record user `Name`, `Section`, `Action Type` (`In`/`Out`), and `Timestamp`
- Track open sessions and prevent duplicate logins
- Store logs in `logins.db` for the CLI and browser local storage for the web UI
- View login/logout history and session history
- Export login/logout history to CSV
- Responsive browser interface with clean styling

## Requirements

- Python 3.8+

## Setup

1. Open the project folder in your terminal.
2. Ensure Python is installed:

```bash
python3 --version
```

3. Run the CLI application:

```bash
python3 main.py
```

4. Open the browser UI by opening `index.html` in a browser.

## How it works

- The application stores data in a SQLite database file named `logins.db` in the project folder.
- There are three tables:
  - `users`: stores each unique user by `name` and `section`.
  - `sessions`: tracks login and logout times for each user.
  - `log_entries`: records every `In` and `Out` action with a timestamp.
- The user enters `Name` and `Section` to log in or log out.
- A login creates a session and appends an `In` log entry.
- A logout closes the active session and appends an `Out` log entry.
- History can be viewed on-screen or exported to `login_history.csv`.

## Usage

- Choose `1` to log in
- Choose `2` to log out
- Choose `3` to view all login/logout events
- Choose `4` to view session history
- Choose `5` to export history to CSV
- Choose `6` to quit
