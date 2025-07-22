import tkinter as tk
from tkinter import ttk

class SettingsTab(tk.Frame):
    """
    The UI for the Settings tab, including profile and LLM configuration.
    """
    PLACEHOLDER_TEXT = "•••••••••••••••••••• (loaded from .env)"

    def __init__(self, master, colors, config, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self.config_data = config
        self.config(bg=self.colors['bg'])
        self.api_key_loaded = self.config_data.get('gemini_api_key') is not None

        self._create_widgets()

    def _create_widgets(self):
        """Creates and lays out the widgets for the settings tab."""
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Profile Settings Section ---
        profile_frame = tk.LabelFrame(main_frame, text="Profile Settings",
                                      bg=self.colors['bg'], fg=self.colors['fg'],
                                      padx=15, pady=10)
        profile_frame.pack(fill=tk.X, pady=(0, 20))

        # Subscription Tier
        tk.Label(profile_frame, text="Subscription Tier:", bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        tk.Label(profile_frame, text="Pro (Placeholder)", bg=self.colors['bg'], fg=self.colors['accent']).grid(row=0, column=1, sticky=tk.W, padx=10)

        # Unorthodox Ideas Slider
        tk.Label(profile_frame, text="Unorthodox Ideas:", bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.chaos_slider = ttk.Scale(profile_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200)
        self.chaos_slider.set(self.config_data.get('unorthodox_ideas', 50))
        self.chaos_slider.grid(row=1, column=1, sticky=tk.W, padx=10)

        # --- LLM Configuration Section ---
        llm_frame = tk.LabelFrame(main_frame, text="LLM Configuration",
                                  bg=self.colors['bg'], fg=self.colors['fg'],
                                  padx=15, pady=10)
        llm_frame.pack(fill=tk.X)

        # Gemini API Key
        tk.Label(llm_frame, text="Gemini API Key:", bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = tk.Entry(llm_frame, textvariable=self.api_key_var, width=50,
                                      bg=self.colors['bg'], fg=self.colors['fg'],
                                      insertbackground=self.colors['fg'],
                                      relief=tk.FLAT, highlightthickness=1,
                                      highlightbackground=self.colors['quote'])

        if self.api_key_loaded:
            self.api_key_var.set(self.PLACEHOLDER_TEXT)
        else:
            self.api_key_entry.config(show="*")

        self.api_key_entry.grid(row=0, column=1, sticky=tk.W, padx=10)
        self.api_key_entry.bind("<FocusIn>", self._on_api_key_focus_in)
        self.api_key_entry.bind("<FocusOut>", self._on_api_key_focus_out)

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

    def get_settings_data(self):
        """Returns a dictionary of the current settings from the UI."""
        current_api_key = self.api_key_var.get()

        if current_api_key == self.PLACEHOLDER_TEXT:
            api_key_to_save = None  # Special value for "no change"
        else:
            api_key_to_save = current_api_key  # Can be a new key or an empty string

        return {
            'gemini_api_key': api_key_to_save,
            'unorthodox_ideas': self.chaos_slider.get()
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
                    if isinstance(grandchild, tk.Label):
                        widget_groups['labels'].append(grandchild)

        for frame in widget_groups['frames'] + widget_groups['labelframes']:
            frame.config(bg=self.colors['bg'])
        for labelframe in widget_groups['labelframes']:
            labelframe.config(fg=self.colors['fg'])
        for label in widget_groups['labels']:
            if label.cget('fg') != self.colors['accent']: # Don't change the accent color label
                label.config(bg=self.colors['bg'], fg=self.colors['fg'])
        for entry in widget_groups['entries']:
            entry.config(bg=self.colors['bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'], highlightbackground=self.colors['quote'])