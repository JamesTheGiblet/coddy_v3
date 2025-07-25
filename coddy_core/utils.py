import sys
import os
import subprocess


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

def resource_path(relative_path):
    """
    Get the absolute path to a resource, which works for both development
    and for a bundled executable (PyInstaller/Nuitka).
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Not running in a bundle, so the base path is the project root.
        # This assumes utils.py is in coddy_core/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_git_commit_hash():
    """
    Retrieves the short git commit hash of the current HEAD.
    Returns 'N/A' if not a git repository or git is not installed.
    """
    try:
        # Assumes this script is in coddy_core/
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        if not os.path.isdir(os.path.join(project_root, ".git")):
            return "N/A"

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=project_root, check=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "N/A"