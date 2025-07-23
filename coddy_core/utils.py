import sys
import os

def get_app_root():
    """
    Determines the root directory of the application, whether it's running
    from source or as a bundled executable (e.g., via PyInstaller).
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # The application is frozen (e.g., by PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # The application is running from a .py file
        return os.getcwd()

def get_log_dir():
    """Returns the absolute path to the log directory."""
    log_dir = os.path.join(get_app_root(), "log")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir