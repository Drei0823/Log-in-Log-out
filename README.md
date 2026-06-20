import sqlite3
from datetime import datetime

# Database setup
DB_NAME = 'user_sessions.db'

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            section TEXT NOT NULL,
            action_type TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_action(name, section, action_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now()
    cursor.execute('''
        INSERT INTO logs (name, section, action_type, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (name, section, action_type, timestamp))
    conn.commit()
    conn.close()

def view_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT name, section, action_type, timestamp FROM logs ORDER BY timestamp DESC')
    logs = cursor.fetchall()
    conn.close()
    return logs

def main():
    create_tables()
    print("Welcome to the User Session Tracking System")
    while True:
        print("\nSelect an option:")
        print("1. Log In")
        print("2. Log Out")
        print("3. View Logs")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            name = input("Enter your full name: ").strip()
            section = input("Enter your section: ").strip()
            log_action(name, section, 'In')
            print(f"{name} logged IN at {datetime.now()}")
        elif choice == '2':
            name = input("Enter your full name: ").strip()
            section = input("Enter your section: ").strip()
            log_action(name, section, 'Out')
            print(f"{name} logged OUT at {datetime.now()}")
        elif choice == '3':
            logs = view_logs()
            print("\n--- Log History ---")
            for log in logs:
                print(f"Name: {log[0]}, Section: {log[1]}, Action: {log[2]}, Time: {log[3]}")
        elif choice == '4':
            print("Exiting the system. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == '__main__':
    main()
