import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog, simpledialog, messagebox
from typing import Self
import theme
import os
import sys

# Ensure main_application is imported
import main_application

class LandingPage(tk.Tk):
    def __init__(self, theme_name='dark', on_start=None, on_load=None):
        """
        Initialize the CoddyLandingPage window.

        Args:
            theme_name (str): The name of the theme to use.
            on_start (callable, optional): Callback for starting a project.
            on_load (callable, optional): Callback for loading a project.
        """
        super().__init__()

        # --- Set Callbacks ---
        # Use the provided on_start function, or the default project creation prompt.
        self.on_start_callback = on_start if on_start else self._prompt_start_project
        # Use the provided on_load function, or the default folder prompt.
        self.on_load_callback = on_load if on_load else self._prompt_load_project
        self.current_theme_name = theme_name

        # --- Window Configuration ---
        self.title("Coddy V3 - Your Vibe-Coding Companion")
        self.geometry("600x450")
        self.resizable(False, False) # Optional: prevent resizing

        # --- Widget Fonts ---
        self.title_font = tkfont.Font(family='Segoe UI', size=22, weight="bold")
        self.tagline_font = tkfont.Font(family='Helvetica', size=14, weight="bold")
        self.body_font = tkfont.Font(family='Helvetica', size=12)
        self.quote_font = tkfont.Font(family='Helvetica', size=11, slant="italic")
        self.button_font = tkfont.Font(family='Helvetica', size=12, weight="bold")

        # --- Widget Holders ---
        self.main_frame = None
        self.title_label = None
        self.tagline_label = None
        self.intro_label = None
        self.quote_label = None
        self.start_button = None
        self.separator = None
        self.load_button = None
        self.theme_buttons = []

        # --- Create and layout widgets ---
        self._create_widgets()
        self.switch_theme(theme_name)

    def _create_widgets(self):
        """Creates and places the static widgets in the window."""
        # --- Theme Switcher ---
        # Pack this first to reserve its space at the bottom
        theme_frame = tk.Frame(self)
        theme_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        dark_button = tk.Button(theme_frame, text="Dark", command=lambda: self.switch_theme('dark'), cursor="hand2")
        light_button = tk.Button(theme_frame, text="Light", command=lambda: self.switch_theme('light'), cursor="hand2")
        weird_button = tk.Button(theme_frame, text="Weird", command=lambda: self.switch_theme('weird'), cursor="hand2")
        
        self.theme_buttons.extend([dark_button, light_button, weird_button])

        # Pack buttons to the right
        light_button.pack(side=tk.RIGHT, padx=(5, 0))
        weird_button.pack(side=tk.RIGHT, padx=(5, 0))
        dark_button.pack(side=tk.RIGHT)

        for btn in self.theme_buttons:
            btn.bind("<Enter>", self._on_theme_button_enter)
            btn.bind("<Leave>", self._on_theme_button_leave)

        # Main content frame
        # This will now fill the remaining space above the theme switcher
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Main Title
        self.title_label = tk.Label(self.main_frame, text="Welcome to Coddy V3", font=self.title_font)
        self.title_label.pack(pady=(10, 5))

        # Tagline from README
        self.tagline_label = tk.Label(self.main_frame, text="Your vibe-coding companion.", font=self.tagline_font)
        self.tagline_label.pack(pady=(0, 25))

        # Introduction Text from README
        intro_text = (
            "Coddy fuses creative coding with AI-powered automation to help you\n"
            "brainstorm, plan, generate, refactor, and evolve projects."
        )
        self.intro_label = tk.Label(self.main_frame, text=intro_text, font=self.body_font, justify=tk.CENTER)
        self.intro_label.pack(pady=10, padx=20)

        # Philosophy Quote from README
        self.quote_label = tk.Label(self.main_frame, text='"Let the AI do the grunt work — you focus on the vibes."', font=self.quote_font)
        self.quote_label.pack(pady=25)

        # Visual Separator
        self.separator = tk.Frame(self.main_frame, height=1)
        self.separator.pack(fill='x', pady=15, padx=40)

        # --- Action Buttons ---
        self.action_frame = tk.Frame(self.main_frame)
        self.action_frame.pack(pady=20)

        # Start a Project Button
        self.start_button = tk.Button(
            self.action_frame,
            text="Start a Project",
            font=self.button_font,
            command=self.on_start_callback,
            padx=15, pady=5,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        self.start_button.bind("<Enter>", self._on_action_button_enter)
        self.start_button.bind("<Leave>", self._on_action_button_leave)

        # Load a Project Button
        self.load_button = tk.Button(
            self.action_frame,
            text="Load a Project",
            font=self.button_font,
            command=self.on_load_callback,
            padx=15, pady=5, relief=tk.FLAT, borderwidth=0,
            cursor="hand2"
        )
        self.load_button.pack(side=tk.LEFT)
        self.load_button.bind("<Enter>", self._on_action_button_enter)
        self.load_button.bind("<Leave>", self._on_action_button_leave)

    def _on_action_button_enter(self, event):
        """Handler for mouse entering an action button."""
        event.widget.config(bg=self.colors['accent_hover'])

    def _on_action_button_leave(self, event):
        """Handler for mouse leaving an action button."""
        event.widget.config(bg=self.colors['accent'])

    def _on_theme_button_enter(self, event):
        """Handler for mouse entering a theme button."""
        event.widget.config(fg=self.colors['fg'])

    def _on_theme_button_leave(self, event):
        """Handler for mouse leaving a theme button."""
        event.widget.config(fg=self.colors['quote'])

    def _prompt_start_project(self):
        """Prompts for a new project name and creates the folder structure."""
        project_name = simpledialog.askstring(
            "Start a New Project",
            "Enter a name for your new project:",
            parent=self
        )

        if not project_name or not project_name.strip():
            print("Project creation cancelled.")
            return

        # Basic sanitization for folder name
        project_name = project_name.strip()
        # In a real app, more robust sanitization would be needed.

        base_path = os.path.join("coddy_codes")
        project_path = os.path.join(base_path, project_name)

        if os.path.exists(project_path):
            load_existing = messagebox.askyesno(
                "Project Exists",
                f"A project named '{project_name}' already exists.\nDo you want to load it?",
                parent=self
            )
            if load_existing:
                self.launch_main_app(project_path)
        else:
            os.makedirs(project_path, exist_ok=True)
            print(f"Created new project at: {project_path}")
            self.launch_main_app(project_path)

    def _prompt_load_project(self):
        """Opens a dialog to select a project folder and prints the path."""
        project_path = filedialog.askdirectory(
            title="Select a Coddy Project Folder",
            mustexist=True
        )
        if project_path:
            self.launch_main_app(project_path)
        else:
            print("No project folder selected.")

    def _on_app_close(self):
        """Handles the main application window closing event."""
        if self.main_app_window:
            self.main_app_window.save_settings()
        self.destroy()

    def launch_main_app(self, project_path):
        """Hides the landing page and opens the main application window."""
        self.main_app_window = None # Clear any previous reference
        self.withdraw() # Hide the landing page
        app_window = main_application.MainApplication(
            master=self,
            project_path=project_path,
            theme_name=self.current_theme_name
        )
        # When the main app window is closed, save settings and exit.
        self.main_app_window = app_window
        app_window.protocol("WM_DELETE_WINDOW", self._on_app_close)

    def switch_theme(self, theme_name):
        """Loads a new theme and applies the colors to all widgets."""
        self.current_theme_name = theme_name
        self.colors = theme.get_theme(theme_name)
        self._apply_colors()

    def _apply_colors(self):
        """Applies the currently loaded self.colors to the UI."""
        self.config(bg=self.colors['bg'])

        # Configure all frames
        for frame in [self.main_frame, self.action_frame]:
            if frame:
                frame.config(bg=self.colors['bg'])

        self.title_label.config(bg=self.colors['bg'], fg=self.colors['accent'])
        self.tagline_label.config(bg=self.colors['bg'], fg=self.colors['fg'])
        self.intro_label.config(bg=self.colors['bg'], fg=self.colors['fg'])
        self.quote_label.config(bg=self.colors['bg'], fg=self.colors['quote'])
        self.separator.config(bg=self.colors['quote'])

        # Configure all main action buttons
        for btn in [self.start_button, self.load_button]:
            if btn:
                btn.config(bg=self.colors['accent'], fg=self.colors['button_fg'],
                           activebackground=self.colors['accent_active'],
                           activeforeground=self.colors['button_fg'])
        
        # Style the theme buttons to be more subtle
        for btn in self.theme_buttons:
            btn.config(bg=self.colors['bg'], fg=self.colors['quote'], relief=tk.FLAT, borderwidth=0, activeforeground=self.colors['fg'])

if __name__ == "__main__":
    # To see the light theme, change 'dark' to 'light'
    # The CoddyLandingPage now handles the load action by default.
    # A custom on_load function can still be passed to override this.
    app = LandingPage(theme_name='dark')
    app.mainloop()