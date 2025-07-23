import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog, simpledialog, messagebox
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    filename=os.path.join(utils.get_log_dir(), "landing_page.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)
# Local imports
from . import config_manager, theme, utils
# Ensure main_application is imported
from . import main_application

class LandingPage(tk.Toplevel):
    def __init__(self, master, theme_name='dark', *args, **kwargs):
        """
        Initialize the CoddyLandingPage window.
        """
        super().__init__(master, *args, **kwargs)
        try:
            self.app_config = config_manager.load_config()
        except Exception as e:
            logger.exception("Failed to load application config.")
            messagebox.showerror("Configuration Error", f"Could not load settings.json: {e}")
            self.app_config = {} # Start with an empty config

        self._perform_first_run_setup()

        self.main_app_window = None
        # When this window is closed, the entire application should exit.
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
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
        logger.info("LandingPage initialized.")

    def _perform_first_run_setup(self):
        """Creates application-level directories and files on the very first run."""
        if not self.app_config.get('has_run_before', False):
            logger.info("Performing first-run shrine setup...")
            try:
                app_root = utils.get_app_root()
                # Create the main directory for user projects
                os.makedirs(os.path.join(app_root, "coddy_codes"), exist_ok=True)
                logger.info("Created 'coddy_codes' directory.")

                # Create the manifesto file in the project root
                manifesto_path = os.path.join(app_root, "manifesto.md")
                if not os.path.exists(manifesto_path):
                    manifesto_content = '''
# Coddy's Manifesto

> “Everyone’s this is me—the way I think, refined, coded, and relayed to the world. I'm weird, odd, and don’t fit in. Coddy lets anyone do what I do—make amazing things.”
'''
                    with open(manifesto_path, 'w', encoding='utf-8') as f:
                        f.write(manifesto_content.strip())
                    logger.info("Created 'manifesto.md'.")
            except OSError as e:
                logger.exception("Error during first-run shrine setup.")
                messagebox.showerror("Setup Error", f"Could not perform first-run setup:\n{e}", parent=self)

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
            font=self.button_font, command=self._prompt_start_project,
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
            font=self.button_font, command=self._prompt_load_project,
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
        logger.info(f"User prompted to start a new project. Entered: '{project_name}'")

        if not project_name or not project_name.strip():
            logger.info("Project creation cancelled by user.")
            print("Project creation cancelled.")
            return

        # Basic sanitization for folder name
        project_name = project_name.strip()
        # In a real app, more robust sanitization would be needed.

        app_root = utils.get_app_root()
        base_path = os.path.join(app_root, "coddy_codes")
        project_path = os.path.join(base_path, project_name)

        if os.path.exists(project_path):
            logger.info(f"Project '{project_name}' already exists.")
            load_existing = messagebox.askyesno(
                "Project Exists",
                f"A project named '{project_name}' already exists.\nDo you want to load it?",
                parent=self
            )
            if load_existing:
                self.launch_main_app(project_path, file_to_open=None)
            else:
                logger.info("User chose not to load existing project.")
        else:
            try:
                os.makedirs(project_path, exist_ok=True)
                logger.info(f"Created new project directory at: {project_path}")
                print(f"Created new project at: {project_path}")

                file_to_open = None
                # Check if this is the user's first time creating a project
                if not self.app_config.get('has_run_before', False):
                    logger.info("First run detected, creating welcome file.")
                    self._create_welcome_file(project_path)
                    file_to_open = "getting_started.md"
                    
                    self.app_config['has_run_before'] = True
                    config_manager.save_config(self.app_config)

                self.launch_main_app(project_path, file_to_open=file_to_open)
            except Exception as e:
                logger.exception(f"Failed to create project '{project_name}' at {project_path}")
                messagebox.showerror("Project Creation Error", f"Could not create project:\n{e}", parent=self)

    def _create_welcome_file(self, project_path):
        """Creates a getting_started.md file in the new project directory."""
        welcome_content = """# Welcome to Coddy!

This is your first project. Here's a quick guide to get you started.

## The Coddy Workflow

Coddy is designed to help you go from idea to code, fast. Here's the typical flow:

### 1. 🌱 Genesis Tab
This is where your project is born. Use the chat to brainstorm your idea. Once it's solid, ask Coddy to **Generate README** or **Generate Roadmap**.

### 2. ✅ Tasks Tab
Once you have a `roadmap.md`, this tab becomes your interactive project plan. Check off tasks as you complete them.

### 3. ✍️ Edit Tab
This is your AI-assisted coding environment. Click on any file in the "Project Files" tree to open it. Use the AI Task box to get suggestions, refactor code, and more.

### 4. ⚙️ Settings Tab
Configure Coddy to your liking. Set your Gemini API key, change the theme, and manage preferences.

---

Happy coding!
"""
        try:
            with open(os.path.join(project_path, "getting_started.md"), 'w', encoding='utf-8') as f:
                f.write(welcome_content)
            logger.info(f"Welcome file created in {project_path}")
        except IOError as e:
            logger.exception(f"Could not create welcome file in {project_path}")
            messagebox.showerror("File Error", f"Could not create welcome file:\n{e}", parent=self)

    def _prompt_load_project(self):
        """Opens a dialog to select a project folder and prints the path."""
        project_path = filedialog.askdirectory(
            title="Select a Coddy Project Folder",
            mustexist=True
        )
        if project_path:
            logger.info(f"User selected project to load: {project_path}")
            self.launch_main_app(project_path, file_to_open=None)
        else:
            logger.info("Project loading cancelled by user.")
            print("No project folder selected.")

    def launch_main_app(self, project_path, file_to_open=None):
        """Hides the landing page and opens the main application window."""
        logger.info(f"Launching main application for project: {project_path}")
        try:
            # Create the main window, which will set its own close protocol
            main_application.MainApplication(
                master=self.master,
                project_path=project_path,
                theme_name=self.current_theme_name,
                file_to_open=file_to_open
            )
            # Destroy the landing page as the main app is now open
            self.destroy()
            logger.info("Landing page destroyed, main application is now active.")
        except Exception as e:
            logger.critical(f"Failed to launch MainApplication for project {project_path}", exc_info=True)
            messagebox.showerror("Application Error", f"A critical error occurred while launching the project:\n{e}", parent=self)

    def switch_theme(self, theme_name):
        """Loads a new theme and applies the colors to all widgets."""
        self.current_theme_name = theme_name
        logger.info(f"Switching theme to '{theme_name}'.")
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