import os
import subprocess
import sys
import shutil

import re
# Add Pillow import for icon conversion
try:
    from PIL import Image
except ImportError:
    Image = None

# Add project root to path to allow importing from coddy_core
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from coddy_core.utils import get_git_commit_hash

# --- Configuration ---
APP_NAME = "CoddyV3"
APP_VERSION = "3.0.0-beta.1" # Should match coddy_core/__init__.py

def get_app_version():
    """Reads the version from coddy_core/version.py to ensure a single source of truth."""
    version_file = os.path.join("coddy_core", "version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        version_file_content = f.read()
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", version_file_content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in coddy_core/version.py")

APP_VERSION = get_app_version()
ENTRY_POINT = "run.py" # Use the top-level runner script for robustness
# Define paths for both PNG (source) and ICO (target)
ICON_PATH = "assets/icon.ico"
ICON_PNG_PATH = "assets/icon.png"
ASSETS_DIR = "assets"
DIST_DIR = "dist"
BUILD_DIR = "build"

def prepare_icon():
    """Converts icon.png to icon.ico if it doesn't exist."""
    if Image and os.path.exists(ICON_PNG_PATH) and not os.path.exists(ICON_PATH):
        print("--> Converting icon.png to icon.ico...")
        img = Image.open(ICON_PNG_PATH)
        img.save(ICON_PATH, format='ICO', sizes=[(256, 256)])

def update_changelog(commit_hash):
    """Updates the changelog with the current commit hash and places it in dist/."""
    print("--> Updating changelog with commit hash...")
    template_path = "changelog.md"
    output_path = os.path.join(DIST_DIR, "changelog.md")
    
    os.makedirs(DIST_DIR, exist_ok=True)

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace("[build-hash-goes-here]", commit_hash)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"    Changelog generated at: {output_path}")

def run_pyinstaller():
    """Runs the PyInstaller command to build the executable."""
    print("\n--> Running PyInstaller...")

    pyinstaller_cmd = shutil.which("pyinstaller")
    if not pyinstaller_cmd:
        print("Error: pyinstaller command not found. Is it installed in your virtual environment?")
        sys.exit(1)

    command = [
        pyinstaller_cmd,
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        "--uac-admin",
    ]
    # Only add the icon if it exists to prevent build errors
    if os.path.exists(ICON_PATH):
        command.extend([f"--icon={ICON_PATH}"])
    else:
        print(f"    Icon not found at '{ICON_PATH}', building without an icon.")

    command.extend([f"--add-data={ASSETS_DIR}{os.pathsep}{ASSETS_DIR}", ENTRY_POINT])

    print(f"    Command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        print("    PyInstaller build successful.")
    except subprocess.CalledProcessError as e:
        print(f"\n--- PyInstaller Build Failed ---")
        print(f"PyInstaller exited with error code {e.returncode}.")
        print("Please check the output above for details.")
        print("----------------------------------")
        sys.exit(1)

def find_makensis():
    """Finds the makensis executable by checking the PATH and common install locations."""
    # First, check if 'makensis' is in the system's PATH
    makensis_path = shutil.which("makensis")
    if makensis_path:
        return makensis_path

    # If not in PATH, check common installation directories on Windows
    if sys.platform == 'win32':
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        program_files_64 = os.environ.get("ProgramW6432", "C:\\Program Files")

        possible_paths = [
            os.path.join(program_files_x86, "NSIS", "makensis.exe"),
            os.path.join(program_files_64, "NSIS", "makensis.exe"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"    Found makensis at: {path}")
                return path

    return None

def run_nsis():
    """Runs the NSIS command to build the installer."""
    print("\n--> Running NSIS...")
    nsis_script = "installer.nsi"

    makensis_cmd = find_makensis()
    if not makensis_cmd:
        print("\n--- NSIS Error ---")
        print("makensis command not found. Is NSIS installed and in your system's PATH?")
        print("Common install paths were also checked.")
        print("Download from: https://nsis.sourceforge.io/Download")
        print("------------------")
        sys.exit(1)

    try:
        # Pass the version to the script via command line define
        command = [makensis_cmd, f"/DAPP_VERSION={APP_VERSION}", nsis_script]
        subprocess.run(command, check=True)
        print("    NSIS installer build successful.")
        print(f"    Installer created at: {os.path.join(DIST_DIR, f'{APP_NAME}_Installer.exe')}")
    except subprocess.CalledProcessError as e:
        # This error means makensis ran but failed. The error message from
        # makensis itself (printed to stdout/stderr above this) is the most
        # important information.
        print(f"\n--- NSIS Build Failed ---")
        print(f"makensis exited with a non-zero exit code: {e.returncode}")
        print("This usually indicates an error in your 'installer.nsi' script.")
        print("Please review the output from makensis above for specific error details.")
        print("---------------------------")
        sys.exit(1)
    except FileNotFoundError:
        # This is a fallback, but find_makensis should prevent it from ever happening.
        print("\n--- NSIS Error ---")
        print(f"The command '{makensis_cmd}' was not found, even after searching common paths.")
        print("Download from: https://nsis.sourceforge.io/Download")
        print("------------------")
        sys.exit(1)

def main():
    """Main build process."""
    print(f"--- Starting Coddy V3 Build Process (v{APP_VERSION}) ---")
    prepare_icon()
    update_changelog(get_git_commit_hash())
    run_pyinstaller()
    run_nsis()
    print("\n--- Build Complete! ---")

if __name__ == "__main__":
    main()