import tkinter as tk
from tkinter import messagebox
import os
import logging
import traceback
from .splash import SplashScreen
from .landing_page import LandingPage
from . import database, utils, config_manager

LOG_FILE = os.path.join(utils.get_log_dir(), "app.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

class App:
    """
    The main application controller. Manages window flow and lifecycle.
    """
    def __init__(self):
        self.root = tk.Tk()
        # Set window icon from the .png file
        try:
            icon_path = utils.resource_path('assets/icon.png')
            self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except tk.TclError:
            logger.warning("Could not load application icon. Is 'assets/icon.png' missing or invalid?")

        self.root.withdraw()  # Hide the root window until the app is ready

        # --- 1. Show Splash Screen ---
        self.splash = SplashScreen(self.root)

        # --- 2. Perform Heavy Initialization ---
        self.root.report_callback_exception = self._handle_exception

        try:
            database.init_db() # Initialize the database on startup
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.critical("FATAL: Could not initialize the database.", exc_info=True)
            messagebox.showerror("Fatal Error", f"Could not initialize the database. The application cannot start.\n\nError: {e}", parent=self.root)
            self.splash.close()
            self.root.destroy()
            self.initialization_failed = True
            return

        self.initialization_failed = False

        # --- Perform First-Run Setup ---
        self._perform_first_run_setup()

        # Log version and commit hash for traceability
        from .version import __version__
        try:
            commit_hash = utils.get_git_commit_hash()
        except Exception:
            # In a bundled app, we won't have git. This is expected.
            commit_hash = "N/A (not in git repo)"
        logger.info("--- Coddy V3 Initializing ---")
        logger.info(f"Version: {__version__}")
        logger.info(f"Commit Hash: {commit_hash}")

    def _handle_exception(self, exc, val, tb):
        """Handles uncaught exceptions in the Tkinter event loop."""
        error_message = "".join(traceback.format_exception(exc, val, tb))
        logger.critical(f"Unhandled exception occurred:\n{error_message}")
        messagebox.showerror("Unhandled Exception", "A critical error occurred. Please check app.log for details.", parent=self.root)

    def _perform_first_run_setup(self):
        """Creates application-level directories and files on the very first run."""
        # This check is now performed at the app level, not the landing page level.
        app_config = config_manager.load_config()
        if not app_config.get('has_run_before', False):
            logger.info("Performing first-run shrine setup...")
            try:
                # The shrine (user projects, manifesto) belongs in a user-writable space.
                shrine_dir = utils.get_user_shrine_dir()
                # The coddy_codes directory now goes inside the shrine.
                os.makedirs(os.path.join(shrine_dir, "coddy_codes"), exist_ok=True)
                logger.info(f"Ensured 'coddy_codes' directory exists in {shrine_dir}.")

                # The manifesto also goes into the shrine.
                manifesto_path = os.path.join(shrine_dir, "manifesto.md")
                if not os.path.exists(manifesto_path):
                    manifesto_content = utils.resource_path("assets/manifesto_template.md")
                    with open(manifesto_content, 'r', encoding='utf-8') as template_f, \
                         open(manifesto_path, 'w', encoding='utf-8') as f:
                        f.write(template_f.read())
                    logger.info(f"Created 'manifesto.md' in {shrine_dir}.")
                
                # Mark the setup as complete
                app_config['has_run_before'] = True
                config_manager.save_config(app_config)
            except Exception as e:
                logger.exception("Error during first-run shrine setup.")
                messagebox.showerror("Setup Error", f"Could not perform first-run setup:\n{e}", parent=self.root)

    def start(self):
        """Starts the application by showing the landing page."""
        if hasattr(self, 'initialization_failed') and self.initialization_failed:
            logger.error("Application start aborted due to initialization failure.")
            return

        # --- 3. Create Main UI ---
        logger.info("Starting application UI.")
        LandingPage(master=self.root)

        # --- 4. Close Splash and Show Main UI ---
        self.splash.close()
        # The LandingPage is a Toplevel and will show itself.

        self.root.mainloop()
        logger.info("Application main loop ended.")