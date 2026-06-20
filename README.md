import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

DB_NAME = 'user_sessions.db'

# Initialize database and tables
def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Logs table for session tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            section TEXT NOT NULL,
            action_type TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    # Active sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            login_time DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Register new user
def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Authenticate user
def authenticate(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Check if user is already logged in
def is_user_logged_in(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM active_sessions WHERE username=?', (username,))
    session = cursor.fetchone()
    conn.close()
    return session

# Log in user
def login_user(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    login_time = datetime.now()
    cursor.execute('INSERT OR IGNORE INTO active_sessions (username, login_time) VALUES (?, ?)', (username, login_time))
    conn.commit()
    conn.close()

# Log out user
def logout_user(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM active_sessions WHERE username=?', (username,))
    conn.commit()
    conn.close()

# Log actions
def log_action(username, section, action_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now()
    cursor.execute('''
        INSERT INTO logs (username, section, action_type, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (username, section, action_type, timestamp))
    conn.commit()
    conn.close()

# Fetch logs
def get_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, section, action_type, timestamp FROM logs ORDER BY timestamp DESC')
    logs = cursor.fetchall()
    conn.close()
    return logs

# GUI Application
class SessionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User Session Tracking System")
        self.current_user = None

        self.create_login_frame()

    def create_login_frame(self):
        self.clear_frame()
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=10, pady=10)

        tk.Label(self.login_frame, text="Username").grid(row=0, column=0, sticky='e')
        tk.Label(self.login_frame, text="Password").grid(row=1, column=0, sticky='e')
        self.username_entry = tk.Entry(self.login_frame)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, pady=5)
        tk.Button(self.login_frame, text="Register", command=self.register).grid(row=2, column=1, pady=5)

    def create_main_frame(self):
        self.clear_frame()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        # Welcome label
        tk.Label(self.main_frame, text=f"Welcome, {self.current_user}").grid(row=0, column=0, columnspan=2)

        # Section entry
        tk.Label(self.main_frame, text="Section").grid(row=1, column=0, sticky='e')
        self.section_entry = tk.Entry(self.main_frame)
        self.section_entry.grid(row=1, column=1)

        # Buttons
        self.login_button = tk.Button(self.main_frame, text="Log In", command=self.log_in)
        self.logout_button = tk.Button(self.main_frame, text="Log Out", command=self.log_out)
        self.view_logs_button = tk.Button(self.main_frame, text="View Logs", command=self.show_logs)

        self.login_button.grid(row=2, column=0, pady=5)
        self.logout_button.grid(row=2, column=1, pady=5)
        self.view_logs_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Active session indicator
        self.session_label = tk.Label(self.main_frame, text="")
        self.session_label.grid(row=4, column=0, columnspan=2)

        # Check if user already logged in
        if is_user_logged_in(self.current_user):
            self.session_label.config(text="Status: Logged In")
        else:
            self.session_label.config(text="Status: Logged Out")

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        if register_user(username, password):
            messagebox.showinfo("Success", "Registration successful. Please log in.")
        else:
            messagebox.showerror("Error", "Username already exists.")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        user = authenticate(username, password)
        if user:
            self.current_user = username
            self.create_main_frame()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def log_in(self):
        section = self.section_entry.get().strip()
        if not section:
            messagebox.showerror("Error", "Please enter your section")
            return
        if is_user_logged_in(self.current_user):
            messagebox.showinfo("Info", "Already logged in.")
            return
        login_user(self.current_user)
        log_action(self.current_user, section, 'In')
        self.session_label.config(text="Status: Logged In")
        messagebox.showinfo("Logged In", f"{self.current_user} logged in successfully.")

    def log_out(self):
        section = self.section_entry.get().strip()
        if not section:
            messagebox.showerror("Error", "Please enter your section")
            return
        if not is_user_logged_in(self.current_user):
            messagebox.showinfo("Info", "Not logged in.")
            return
        log_action(self.current_user, section, 'Out')
        logout_user(self.current_user)
        self.session_label.config(text="Status: Logged Out")
        messagebox.showinfo("Logged Out", f"{self.current_user} logged out successfully.")

    def show_logs(self):
        logs = get_logs()
        log_window = tk.Toplevel(self.root)
        log_window.title("Logs")
        cols = ('Username', 'Section', 'Action', 'Time')
        tree = ttk.Treeview(log_window, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
        for log in logs:
            tree.insert('', 'end', values=log)
        tree.pack(fill='both', expand=True)

if __name__ == '__main__':
    create_tables()
    root = tk.Tk()
    app = SessionApp(root)
    root.mainloop()
