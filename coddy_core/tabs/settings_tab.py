import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from .. import auth, subscription, theme, config_manager, utils

LOG_FILE = os.path.join(utils.get_log_dir(), "settings_tab.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class SettingsTab(tk.Frame):
    """
    The UI for the Settings tab, where users can manage API keys, themes,
    and subscription tiers for local testing.
    """
    def __init__(self, master, colors, app_logic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self.app_logic = app_logic
        self.config(bg=self.colors['bg'])

        self._create_widgets()
        self.load_settings()
        self.update_auth_status() # Set initial auth state
        logger.info("SettingsTab initialized.")

    def _create_widgets(self):
        """Creates and lays out the widgets for the settings tab."""
        self.columnconfigure(1, weight=1)

        # --- Gemini API Key ---
        ttk.Label(self, text="Gemini API Key:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.api_key_entry = ttk.Entry(self, show="*", width=50)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.api_key_entry.bind("<FocusIn>", self._on_api_key_focus_in)
        self.api_key_entry.bind("<FocusOut>", self._on_api_key_focus_out)

        # --- Theme Selection ---
        ttk.Label(self, text="Theme:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(self, textvariable=self.theme_var, values=theme.get_theme_names(), state="readonly")
        self.theme_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)

        # --- Subscription Tier (for local testing) ---
        ttk.Label(self, text="Subscription Tier (Testing):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.tier_var = tk.StringVar()
        self.tier_combo = ttk.Combobox(self, textvariable=self.tier_var, values=subscription.SubscriptionTier.get_tier_names(), state="readonly")
        self.tier_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.tier_combo.bind("<<ComboboxSelected>>", self._on_tier_change)

        # --- Developer Preferences ---
        dev_frame = ttk.LabelFrame(self, text="Developer Preferences", padding=(10, 5))
        dev_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.autosave_var = tk.BooleanVar()
        self.autosave_check = ttk.Checkbutton(dev_frame, text="Enable Autosave on modification", variable=self.autosave_var)
        self.autosave_check.pack(anchor="w", padx=5)

        self.debug_info_var = tk.BooleanVar()
        self.debug_info_check = ttk.Checkbutton(dev_frame, text="Show Debug Info in console", variable=self.debug_info_var)
        self.debug_info_check.pack(anchor="w", padx=5)

        # --- Authentication Section ---
        auth_frame = ttk.LabelFrame(self, text="Authentication", padding=(10, 5))
        auth_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        auth_frame.columnconfigure(1, weight=1)

        self.auth_status_label = ttk.Label(auth_frame, text="Status: Logged Out")
        self.auth_status_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.login_logout_button = ttk.Button(auth_frame, text="Login...", command=self.app_logic.show_login_window)
        self.login_logout_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

    def load_settings(self):
        """Loads settings from the config manager and populates the widgets."""
        try:
            config = self.app_logic.app_config
            
            # API Key
            api_key = config.get('gemini_api_key', '')
            if api_key:
                self.api_key_entry.insert(0, api_key)
                self._on_api_key_focus_out(None) # To mask it initially
            else:
                self.api_key_entry.insert(0, "Enter your Gemini API key...")
                logger.warning("Gemini API key not found in config.")

            # Theme
            self.theme_var.set(config.get('theme', 'dark'))

            # Tier
            self.tier_var.set(self.app_logic.active_tier_name)

            # Developer Prefs
            self.autosave_var.set(config.get('developer_autosave', False))
            self.debug_info_var.set(config.get('developer_debug_info', False))
            logger.info("Settings loaded into UI.")
        except Exception as e:
            logger.exception(f"Error loading settings: {e}")
            messagebox.showerror("Settings Error", f"Could not load settings: {e}")

    def get_settings_data(self):
        """Returns a dictionary of the current settings from the UI."""
        api_key = self.api_key_entry.get()
        return {
            'gemini_api_key': api_key if "..." not in api_key else None, # Don't save placeholder
            'theme': self.theme_var.get(),
            'active_tier': self.tier_var.get(),
            'developer_autosave': self.autosave_var.get(),
            'developer_debug_info': self.debug_info_var.get(),
        }

    def update_auth_status(self):
        """Updates the UI based on the current authentication state."""
        user = self.app_logic.current_user
        if user:
            self.auth_status_label.config(text=f"Status: Logged in as {user.email} ({user.tier.value})")
            self.login_logout_button.config(text="Logout", command=self.app_logic.logout)
            self.tier_combo.set(user.tier.value)
            self.tier_combo.config(state="disabled")
            logger.info(f"Auth status updated: Logged in as {user.email}")
        else:
            self.auth_status_label.config(text="Status: Logged Out")
            self.login_logout_button.config(text="Login...", command=self.app_logic.show_login_window)
            self.tier_combo.config(state="readonly")
            # When logging out, set the combo to the saved config value
            self.tier_combo.set(self.app_logic.app_config.get('active_tier', 'Free'))
            logger.info("Auth status updated: Logged out.")

    def _on_theme_change(self, event=None):
        """Callback for when the theme is changed."""
        new_theme = self.theme_var.get()
        logger.info(f"Theme changed to: {new_theme}")
        self.app_logic.switch_theme(new_theme)

    def _on_tier_change(self, event=None):
        """Callback for when the tier is changed for local testing."""
        # This only has an effect when logged out.
        new_tier_name = self.tier_var.get()
        logger.info(f"Testing tier changed to: {new_tier_name}")
        self.app_logic.active_tier = subscription.get_tier_by_name(new_tier_name)
        self.app_logic.active_tier_name = new_tier_name # Keep name in sync
        self.app_logic.update_status(f"Testing tier set to: {new_tier_name}")
        self.app_logic.update_all_auth_dependent_ui()

    def _on_api_key_focus_in(self, event):
        """Handler for when the API key entry gets focus."""
        if "..." in self.api_key_entry.get():
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.config(show="*")

    def _on_api_key_focus_out(self, event):
        """Handler for when the API key entry loses focus."""
        if not self.api_key_entry.get():
            self.api_key_entry.config(show="")
            self.api_key_entry.insert(0, "Enter your Gemini API key...")
        else:
            self.api_key_entry.config(show="*")

    def apply_colors(self, colors):
        """Applies a new color theme to the settings tab."""
        self.colors = colors
        self.config(bg=colors['bg'])
        for child in self.winfo_children():
            if isinstance(child, (ttk.Label, ttk.Checkbutton, ttk.LabelFrame)):
                child.configure(background=colors['bg'], foreground=colors['fg'])
            if isinstance(child, ttk.LabelFrame):
                for grandchild in child.winfo_children():
                     if isinstance(grandchild, (ttk.Label, ttk.Checkbutton)):
                        grandchild.configure(background=colors['bg'], foreground=colors['fg'])
        
        self.auth_status_label.config(foreground=self.colors['quote'])