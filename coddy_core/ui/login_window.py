import tkinter as tk
from tkinter import ttk, messagebox
from .. import auth

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

    def _create_login_widgets(self):
        self._clear_frame()
        self.title("Login to Coddy")

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
        
        user = auth.login(email, password)
        if user:
            self.user = user
            self.on_success_callback(self.user)
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.", parent=self)

    def _perform_signup(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showwarning("Input Required", "Please enter both email and password.", parent=self)
            return

        user = auth.signup(email, password)
        if user:
            messagebox.showinfo("Success", "Account created! Please log in to continue.", parent=self)
            self._create_login_widgets()
        else:
            messagebox.showerror("Signup Failed", "An account with this email already exists.", parent=self)

    def _clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()