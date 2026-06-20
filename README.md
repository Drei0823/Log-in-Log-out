import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import datetime

# Initialize database
conn = sqlite3.connect('user_sessions.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    section TEXT NOT NULL,
    login_time TEXT NOT NULL,
    logout_time TEXT,
    FOREIGN KEY (username) REFERENCES users(username)
)
''')
conn.commit()

class UserSessionApp:
    def __init__(self, master):
        self.master = master
        master.title("User Session Tracking System")
        master.geometry("400x300")
        self.current_user = None
        self.current_session_id = None

        self.create_login_register_frame()

    def create_login_register_frame(self):
        self.clear_frame()
        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=50)

        tk.Label(self.frame, text="Username").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.frame, text="Password").grid(row=1, column=0, padx=5, pady=5)

        self.username_entry = tk.Entry(self.frame)
        self.password_entry = tk.Entry(self.frame, show='*')

        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.frame, text="Login", command=self.login).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(self.frame, text="Register", command=self.register).grid(row=2, column=1, padx=5, pady=5)

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        if cursor.fetchone():
            self.current_user = username
            self.create_user_menu()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def create_user_menu(self):
        self.clear_frame()
        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=20)

        tk.Label(self.frame, text=f"Welcome, {self.current_user}").pack(pady=10)

        tk.Label(self.frame, text="Section Name").pack()
        self.section_entry = tk.Entry(self.frame)
        self.section_entry.pack(pady=5)

        tk.Button(self.frame, text="Log In", command=self.start_session).pack(pady=5)
        tk.Button(self.frame, text="Log Out", command=self.end_session).pack(pady=5)
        tk.Button(self.frame, text="View Logs", command=self.view_logs).pack(pady=5)
        tk.Button(self.frame, text="Logout from System", command=self.logout).pack(pady=5)

    def start_session(self):
        if self.is_user_logged_in():
            messagebox.showwarning("Warning", "You are already logged in.")
            return
        section = self.section_entry.get()
        if not section:
            messagebox.showerror("Error", "Please enter a section name")
            return
        login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO sessions (username, section, login_time) VALUES (?, ?, ?)",
                       (self.current_user, section, login_time))
        conn.commit()
        self.current_session_id = cursor.lastrowid
        messagebox.showinfo("Success", f"Logged in to section '{section}' at {login_time}")

    def end_session(self):
        if not self.is_user_logged_in():
            messagebox.showwarning("Warning", "You are not logged in.")
            return
        logout_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE sessions SET logout_time=? WHERE id=?", (logout_time, self.current_session_id))
        conn.commit()
        messagebox.showinfo("Success", f"Logged out at {logout_time}")
        self.current_session_id = None

    def is_user_logged_in(self):
        return self.current_session_id is not None

    def view_logs(self):
        logs_window = tk.Toplevel(self.master)
        logs_window.title("Session Logs")
        logs_window.geometry("600x400")
        tree = ttk.Treeview(logs_window, columns=("ID", "User", "Section", "Login Time", "Logout Time"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("User", text="User")
        tree.heading("Section", text="Section")
        tree.heading("Login Time", text="Login Time")
        tree.heading("Logout Time", text="Logout Time")
        tree.pack(fill=tk.BOTH, expand=True)

        cursor.execute("SELECT * FROM sessions")
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

    def logout(self):
        self.current_user = None
        self.current_session_id = None
        self.create_login_register_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserSessionApp(root)
    root.mainloop()

# Close database connection when the program ends
conn.close()
