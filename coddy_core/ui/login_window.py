import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from .. import auth

# Set up logging
LOG_DIR = r"C:\Users\gilbe\Documents\GitHub\coddy_v3\coddy_core\log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "login_window.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class LoginWindow(tk.Toplevel):
    """A modal window for user login and signup."""

    def __init__(self, master, on_success_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Login to Coddy")
        self.geometry("350x250")
        self.resizable(False, False)

        # Make window modal
        self.transient(master)
        self.grab_set()

        self.user = None
        self.on_success_callback = on_success_callback

        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_login_widgets()
        logger.info("Login window opened.")

    def _create_login_widgets(self):
        self._clear_frame()
        self.title("Login to Coddy")
        logger.info("Switched to login view.")

        ttk.Label(self.main_frame, text="Email:").pack(fill='x', pady=(0, 5))
        self.email_entry = ttk.Entry(self.main_frame)
        self.email_entry.pack(fill='x', pady=(0, 10))
        self.email_entry.focus_set()

        ttk.Label(self.main_frame, text="Password:").pack(fill='x', pady=(0, 5))
        self.password_entry = ttk.Entry(self.main_frame, show="*")
        self.password_entry.pack(fill='x', pady=(0, 20))

        login_button = ttk.Button(self.main_frame, text="Login", command=self._perform_login)
        login_button.pack(fill='x')

        switch_button = ttk.Button(self.main_frame, text="Don't have an account? Sign Up", style="Link.TButton", command=self._create_signup_widgets)
        switch_button.pack(pady=(10, 0))

    def _create_signup_widgets(self):
        self._clear_frame()
        self.title("Sign Up for Coddy")
        logger.info("Switched to signup view.")

        ttk.Label(self.main_frame, text="Email:").pack(fill='x', pady=(0, 5))
        self.email_entry = ttk.Entry(self.main_frame)
        self.email_entry.pack(fill='x', pady=(0, 10))
        self.email_entry.focus_set()

        ttk.Label(self.main_frame, text="Password:").pack(fill='x', pady=(0, 5))
        self.password_entry = ttk.Entry(self.main_frame, show="*")
        self.password_entry.pack(fill='x', pady=(0, 20))

        signup_button = ttk.Button(self.main_frame, text="Sign Up", command=self._perform_signup)
        signup_button.pack(fill='x')

        switch_button = ttk.Button(self.main_frame, text="Already have an account? Login", style="Link.TButton", command=self._create_login_widgets)
        switch_button.pack(pady=(10, 0))

    def _perform_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        logger.info(f"Login attempt for user: {email}")

        try:
            user = auth.login(email, password)
            if user:
                self.user = user
                self.on_success_callback(self.user)
                logger.info(f"Login successful for user: {email}")
                self.destroy()
            else:
                logger.warning(f"Login failed for user {email}: Invalid credentials.")
                messagebox.showerror("Login Failed", "Invalid email or password.", parent=self)
        except Exception as e:
            logger.exception(f"An unexpected error occurred during login for {email}: {e}")
            messagebox.showerror("Login Error", f"An unexpected error occurred: {e}", parent=self)

    def _perform_signup(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        logger.info(f"Signup attempt for user: {email}")

        if not email or not password:
            logger.warning("Signup attempt failed: email or password was empty.")
            messagebox.showwarning("Input Required", "Please enter both email and password.", parent=self)
            return

        try:
            user = auth.signup(email, password)
            if user:
                logger.info(f"Signup successful for user: {email}")
                messagebox.showinfo("Success", "Account created! Please log in to continue.", parent=self)
                self._create_login_widgets()
            else:
                logger.warning(f"Signup failed for user {email}: user already exists.")
                messagebox.showerror("Signup Failed", "An account with this email already exists.", parent=self)
        except Exception as e:
            logger.exception(f"An unexpected error occurred during signup for {email}: {e}")
            messagebox.showerror("Signup Error", f"An unexpected error occurred: {e}", parent=self)

    def _clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()