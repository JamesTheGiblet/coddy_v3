import sys
import os
import subprocess


def get_app_root():
    """
    Determines the root directory of the application, whether it's running
    from source or as a bundled executable (e.g., via PyInstaller).
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # The application is frozen (e.g., by PyInstaller).
        # The executable is in the root of the distribution.
        return os.path.dirname(sys.executable)
    else:
        # The application is running from a .py file.
        # The project root is one level up from this file's directory (coddy_core/).
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_app_data_dir():
    r"""
    Returns the absolute path to the application's data directory.
    This is a user-writable location for logs, configs, etc.
    - Windows: %APPDATA%\Coddy
    - macOS: ~/Library/Application Support/Coddy
    - Linux: ~/.config/Coddy or ~/.local/share/Coddy
    """
    app_name = "Coddy"
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"], app_name)
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", app_name)
    else:
        # Use XDG_CONFIG_HOME if available, otherwise default to ~/.config
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            return os.path.join(xdg_config_home, app_name)
        return os.path.join(os.path.expanduser("~"), ".config", app_name)

def get_log_dir():
    """Returns the absolute path to the log directory inside AppData."""
    log_dir = os.path.join(get_app_data_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def get_user_shrine_dir():
    """
    Returns the absolute path to the user's Coddy shrine directory,
    typically in their Documents folder, creating it if it doesn't exist.
    This is the designated location for user-generated projects and content.
    """
    # A common and reliable way to get the user's home directory.
    home_dir = os.path.expanduser('~')
    # We'll place the shrine in a "Coddy Projects" folder inside Documents.
    shrine_path = os.path.join(home_dir, 'Documents', 'Coddy Projects')
    os.makedirs(shrine_path, exist_ok=True)
    return shrine_path

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