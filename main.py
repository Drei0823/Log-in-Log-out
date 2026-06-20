#!/usr/bin/env python3
import csv
import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("logins.db")

SQL_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    section TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(name, section)
);
"""

SQL_CREATE_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_time TEXT NOT NULL,
    logout_time TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""

SQL_CREATE_LOG_ENTRIES = """
CREATE TABLE IF NOT EXISTS log_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK(action_type IN ('In', 'Out')),
    timestamp TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""


class LoginLogoutDatabase:
    def __init__(self, path: Path):
        self.path = path
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self):
        cursor = self.conn.cursor()
        cursor.execute(SQL_CREATE_USERS)
        cursor.execute(SQL_CREATE_SESSIONS)
        cursor.execute(SQL_CREATE_LOG_ENTRIES)
        self.conn.commit()

    def get_or_create_user(self, name: str, section: str) -> sqlite3.Row:
        name = name.strip()
        section = section.strip()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE name = ? AND section = ?",
            (name, section),
        )
        row = cursor.fetchone()
        if row:
            return row

        timestamp = _current_timestamp()
        cursor.execute(
            "INSERT INTO users (name, section, created_at) VALUES (?, ?, ?)",
            (name, section, timestamp),
        )
        self.conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

    def get_open_session(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM sessions WHERE user_id = ? AND logout_time IS NULL ORDER BY login_time DESC LIMIT 1",
            (user_id,),
        )
        return cursor.fetchone()

    def create_session(self, user_id: int, login_time: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (user_id, login_time) VALUES (?, ?)",
            (user_id, login_time),
        )
        self.conn.commit()

    def close_session(self, user_id: int, logout_time: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE sessions SET logout_time = ? WHERE user_id = ? AND logout_time IS NULL",
            (logout_time, user_id),
        )
        self.conn.commit()
        return cursor.rowcount

    def add_log_entry(self, user_id: int, action_type: str, timestamp: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO log_entries (user_id, action_type, timestamp) VALUES (?, ?, ?)",
            (user_id, action_type, timestamp),
        )
        self.conn.commit()

    def fetch_log_history(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                log_entries.id,
                users.name,
                users.section,
                log_entries.action_type,
                log_entries.timestamp
            FROM log_entries
            JOIN users ON users.id = log_entries.user_id
            ORDER BY log_entries.timestamp ASC
            """
        )
        return cursor.fetchall()

    def fetch_session_history(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                sessions.id,
                users.name,
                users.section,
                sessions.login_time,
                sessions.logout_time
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            ORDER BY sessions.login_time ASC
            """
        )
        return cursor.fetchall()


def _current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _prompt_user_details():
    name = input("Enter full name: ").strip()
    section = input("Enter section: ").strip()
    if not name or not section:
        print("Name and section cannot be empty. Please try again.")
        return None, None
    return name, section


def log_in(db: LoginLogoutDatabase):
    name, section = _prompt_user_details()
    if not name:
        return

    user = db.get_or_create_user(name, section)
    open_session = db.get_open_session(user["id"])
    if open_session:
        print(f"User '{user['name']}' is already logged in since {open_session['login_time']}.")
        print("Please log out before creating a new login entry.")
        return

    timestamp = _current_timestamp()
    db.create_session(user["id"], timestamp)
    db.add_log_entry(user["id"], "In", timestamp)
    print(f"Logged In: {user['name']} ({user['section']}) at {timestamp}")


def log_out(db: LoginLogoutDatabase):
    name, section = _prompt_user_details()
    if not name:
        return

    user = db.get_or_create_user(name, section)
    open_session = db.get_open_session(user["id"])
    if not open_session:
        print(f"No open login session found for {user['name']} in {user['section']}.")
        print("Please log in first before logging out.")
        return

    timestamp = _current_timestamp()
    closed = db.close_session(user["id"], timestamp)
    if closed:
        db.add_log_entry(user["id"], "Out", timestamp)
        print(f"Logged Out: {user['name']} ({user['section']}) at {timestamp}")
    else:
        print("Unable to close the session. Try again.")


def view_logs(db: LoginLogoutDatabase):
    entries = db.fetch_log_history()
    if not entries:
        print("No login/logout history available.")
        return

    print("\nLogin/Logout History")
    print("----------------------")
    for row in entries:
        print(f"{row['timestamp']} | {row['name']} | {row['section']} | {row['action_type']}")
    print()


def export_logs(db: LoginLogoutDatabase):
    default_path = Path.cwd() / "login_history.csv"
    file_path = input(f"Enter export file path [{default_path}]: ").strip() or str(default_path)
    records = db.fetch_log_history()
    if not records:
        print("No logs available to export.")
        return

    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Timestamp", "Name", "Section", "Action Type"])
        for row in records:
            writer.writerow([row["timestamp"], row["name"], row["section"], row["action_type"]])

    print(f"Exported {len(records)} log rows to: {file_path}")


def view_sessions(db: LoginLogoutDatabase):
    sessions = db.fetch_session_history()
    if not sessions:
        print("No session history available.")
        return

    print("\nSession History")
    print("----------------")
    for row in sessions:
        logout_time = row["logout_time"] or "[OPEN SESSION]"
        print(f"{row['login_time']} -> {logout_time} | {row['name']} | {row['section']}")
    print()


def show_menu():
    print("\nLog-In / Log-Out System")
    print("========================")
    print("1. Log In")
    print("2. Log Out")
    print("3. View Log History")
    print("4. View Session History")
    print("5. Export Log History to CSV")
    print("6. Quit")


def main():
    db = LoginLogoutDatabase(DB_PATH)

    while True:
        show_menu()
        choice = input("Choose an option (1-6): ").strip()
        if choice == "1":
            log_in(db)
        elif choice == "2":
            log_out(db)
        elif choice == "3":
            view_logs(db)
        elif choice == "4":
            view_sessions(db)
        elif choice == "5":
            export_logs(db)
        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
