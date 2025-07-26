import sys
import os

# Add the project root to the Python path to ensure coddy_core can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coddy_core.app import App

if __name__ == "__main__":
    """
    Main entry point for running the Coddy application.
    This script ensures that the 'coddy_core' package is correctly
    imported and then starts the application.
    """
    try:
        app = App()
        # Only start the main loop if initialization didn't fail
        if not (hasattr(app, 'initialization_failed') and app.initialization_failed):
            app.start()
    except Exception:
        import traceback
        import tkinter as tk
        from tkinter import messagebox

        # Create a tiny root window to show the error message
        root = tk.Tk()
        root.withdraw()
        error_message = traceback.format_exc()
        print(error_message)  # Also print to console if available
        messagebox.showerror(
            "Fatal Application Error",
            f"Coddy V3 encountered a critical error and must close.\n\n"
            f"Please report this issue.\n\nDetails:\n{error_message}"
        )
        sys.exit(1)