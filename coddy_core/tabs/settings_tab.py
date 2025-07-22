import tkinter as tk
from tkinter import ttk
from .. import subscription, theme

class SettingsTab(tk.Frame):
    """
    The UI for the Settings tab.
    """
    PLACEHOLDER_TEXT = "•••••••••••••••••••• (loaded from .env)"

    def __init__(self, master, colors, app_logic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self.app_logic = app_logic
        self.config_data = app_logic.app_config
        self.config(bg=self.colors['bg'])
        self.api_key_loaded = self.config_data.get('gemini_api_key') is not None

        self._create_widgets()
        self._load_settings() # Load initial values

    def _create_widgets(self):
        """Creates and lays out the widgets for the settings tab."""
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Account Section ---
        account_frame = tk.LabelFrame(main_frame, text="Account",
                                      bg=self.colors['bg'], fg=self.colors['fg'],
                                      padx=15, pady=10)
        account_frame.pack(fill=tk.X, pady=(0, 20))

        self.user_status_label = tk.Label(account_frame, text="Status: Logged Out", bg=self.colors['bg'], fg=self.colors['fg'])
        self.user_status_label.pack(side=tk.LEFT)

        self.auth_button = ttk.Button(account_frame, text="Login", command=self.app_logic.show_login_window)
        self.auth_button.pack(side=tk.RIGHT)

        # --- Profile Settings Section ---
        profile_frame = tk.LabelFrame(main_frame, text="Profile Settings",
                                      bg=self.colors['bg'], fg=self.colors['fg'],
                                      padx=15, pady=10)
        profile_frame.pack(fill=tk.X, pady=(0, 20))

        # Subscription Tier (for local testing when logged out)
        tk.Label(profile_frame, text="Active Tier (for testing):", bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tier_var = tk.StringVar()
        self.tier_combobox = ttk.Combobox(
            profile_frame,
            textvariable=self.tier_var,
            values=subscription.SubscriptionTier.get_tier_names(),
            state='readonly'
        )
        self.tier_combobox.grid(row=0, column=1, sticky=tk.W, padx=10)

        # Unorthodox Ideas Slider
        tk.Label(profile_frame, text="Unorthodox Ideas:", bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.chaos_slider = ttk.Scale(profile_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200)
        self.chaos_slider.grid(row=1, column=1, sticky=tk.W, padx=10)

        # Theme Switcher
        tk.Label(profile_frame, text="Theme:", bg=self.colors['bg'], fg=self.colors['fg']).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar()
        self.theme_combobox = ttk.Combobox(
            profile_frame,
            textvariable=self.theme_var,
            values=theme.get_theme_names(),
            state='readonly'
        )
        self.theme_combobox.grid(row=2, column=1, sticky=tk.W, padx=10)
        self.theme_combobox.bind("<<ComboboxSelected>>", self._on_theme_selected)

        # --- LLM Configuration Section ---
        llm_frame = tk.LabelFrame(main_frame, text="LLM Configuration",
                                  bg=self.colors['bg'], fg=self.colors['fg'],
                                  padx=15, pady=10)
        llm_frame.pack(fill=tk.X, pady=(0, 20))

        # Gemini API Key
        tk.Label(llm_frame, text="Gemini API Key:", bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = tk.Entry(llm_frame, textvariable=self.api_key_var, width=50,
                                      bg=self.colors['bg'], fg=self.colors['fg'],
                                      insertbackground=self.colors['fg'], # Cursor color
                                      relief=tk.FLAT, highlightthickness=1,
                                      highlightbackground=self.colors['quote'])

        if self.api_key_loaded:
            self.api_key_var.set(self.PLACEHOLDER_TEXT)
        else:
            self.api_key_entry.config(show="*")

        self.api_key_entry.grid(row=0, column=1, sticky=tk.W, padx=10)
        self.api_key_entry.bind("<FocusIn>", self._on_api_key_focus_in)
        self.api_key_entry.bind("<FocusOut>", self._on_api_key_focus_out)

        # --- Developer Preferences Section ---
        dev_frame = tk.LabelFrame(main_frame, text="Developer Preferences",
                                  bg=self.colors['bg'], fg=self.colors['fg'],
                                  padx=15, pady=10)
        dev_frame.pack(fill=tk.X)

        self.autosave_var = tk.BooleanVar()
        self.autosave_check = ttk.Checkbutton(dev_frame, text="Enable Autosave on file change", variable=self.autosave_var)
        self.autosave_check.pack(anchor=tk.W)

        self.debug_info_var = tk.BooleanVar()
        self.debug_info_check = ttk.Checkbutton(dev_frame, text="Show debug info in console", variable=self.debug_info_var)
        self.debug_info_check.pack(anchor=tk.W)

    def _on_api_key_focus_in(self, event):
        """Clear placeholder on focus and set show='*'."""
        if self.api_key_var.get() == self.PLACEHOLDER_TEXT:
            self.api_key_var.set("")
            self.api_key_entry.config(show="*")

    def _on_api_key_focus_out(self, event):
        """Restore placeholder if field is empty and a key was originally loaded."""
        if not self.api_key_var.get() and self.api_key_loaded:
            self.api_key_var.set(self.PLACEHOLDER_TEXT)
            self.api_key_entry.config(show="") # Hide the '*' for placeholder

    def _load_settings(self):
        """Loads settings from config into UI widgets."""
        # Load subscription tier
        current_tier = self.config_data.get('active_tier', subscription.SubscriptionTier.FREE.value)
        self.tier_var.set(current_tier)
        # Load unorthodox ideas value
        self.chaos_slider.set(self.config_data.get('unorthodox_ideas', 50))
        # Load current theme
        self.theme_var.set(self.app_logic.theme_name)
        # Load developer preferences
        self.autosave_var.set(self.config_data.get('developer_autosave', False))
        self.debug_info_var.set(self.config_data.get('developer_debug_info', False))
        # Update auth status display
        self.update_auth_status()

    def update_auth_status(self):
        """Updates the UI to reflect the current login status."""
        if self.app_logic.current_user:
            user = self.app_logic.current_user
            self.user_status_label.config(text=f"Logged in as: {user.email} ({user.tier.value})")
            self.auth_button.config(text="Logout", command=self.app_logic.logout)
            self.tier_combobox.config(state="disabled")
        else:
            self.user_status_label.config(text="Status: Logged Out")
            self.auth_button.config(text="Login", command=self.app_logic.show_login_window)
            self.tier_combobox.config(state="readonly")

    def _on_theme_selected(self, event=None):
        """Handles theme selection change and applies it immediately."""
        new_theme = self.theme_var.get()
        self.app_logic.switch_theme(new_theme)

    def get_settings_data(self):
        """Returns a dictionary of the current settings from the UI."""
        current_api_key = self.api_key_var.get()

        if current_api_key == self.PLACEHOLDER_TEXT:
            api_key_to_save = None  # Special value for "no change"
        else:
            api_key_to_save = current_api_key  # Can be a new key or an empty string

        return {
            'gemini_api_key': api_key_to_save,
            'unorthodox_ideas': self.chaos_slider.get(),
            'active_tier': self.tier_var.get(),
            'developer_autosave': self.autosave_var.get(),
            'developer_debug_info': self.debug_info_var.get()
        }

    def apply_colors(self, colors):
        """Applies a new color theme to the settings tab and its children."""
        self.colors = colors
        self.config(bg=self.colors['bg'])

        # Recursively apply colors to all child widgets
        widget_groups = {
            'frames': [self, self.winfo_children()[0]], # self and main_frame
            'labelframes': [],
            'labels': [],
            'entries': [self.api_key_entry]
        }

        for child in self.winfo_children()[0].winfo_children(): # Children of main_frame
            if isinstance(child, tk.LabelFrame):
                widget_groups['labelframes'].append(child)
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label) and grandchild != self.user_status_label:
                        widget_groups['labels'].append(grandchild)

        for frame in widget_groups['frames'] + widget_groups['labelframes']:
            frame.config(bg=self.colors['bg'])
        for labelframe in widget_groups['labelframes']:
            labelframe.config(fg=self.colors['fg'])
        for label in widget_groups['labels'] + [self.user_status_label]:
            label.config(bg=self.colors['bg'], fg=self.colors['fg'])
        for entry in widget_groups['entries']:
            entry.config(bg=self.colors['bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'], highlightbackground=self.colors['quote'])