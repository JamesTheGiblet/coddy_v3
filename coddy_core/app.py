import tkinter as tk
from tkinter import messagebox
import os
import logging
import traceback
from .landing_page import LandingPage
from . import database, utils

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
        self.root.withdraw() # Hide the root window, it only serves as a parent
        self.root.report_callback_exception = self._handle_exception

        try:
            database.init_db() # Initialize the database on startup
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.critical("FATAL: Could not initialize the database.", exc_info=True)
            messagebox.showerror("Fatal Error", f"Could not initialize the database. The application cannot start.\n\nError: {e}", parent=self.root)
            self.root.destroy()
            self.initialization_failed = True
            return

        self.initialization_failed = False
        logger.info("Application initialized.")

    def _handle_exception(self, exc, val, tb):
        """Handles uncaught exceptions in the Tkinter event loop."""
        error_message = "".join(traceback.format_exception(exc, val, tb))
        logger.critical(f"Unhandled exception occurred:\n{error_message}")
        messagebox.showerror("Unhandled Exception", "A critical error occurred. Please check app.log for details.", parent=self.root)

    def start(self):
        """Starts the application by showing the landing page."""
        if hasattr(self, 'initialization_failed') and self.initialization_failed:
            logger.error("Application start aborted due to initialization failure.")
            return
        logger.info("Starting application UI.")
        LandingPage(master=self.root)
        self.root.mainloop()
        logger.info("Application main loop ended.")

if __name__ == "__main__":
    app = App()
    app.start()