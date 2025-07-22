import json
import os

# NOTE: This manager uses the python-dotenv library.
# Ensure it is installed: pip install python-dotenv
from dotenv import load_dotenv, set_key

CONFIG_DIR = ".coddy"
CONFIG_FILE = "settings.json"

# Assume the script is run from the project root, where .coddy and .env reside.
PROJECT_ROOT = os.getcwd() 
CONFIG_PATH = os.path.join(PROJECT_ROOT, CONFIG_DIR, CONFIG_FILE)
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

def _ensure_config_dir_exists():
    """Ensures the .coddy configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    """Loads the application configuration from settings.json."""
    _ensure_config_dir_exists()
    if not os.path.exists(CONFIG_PATH):
        return {}  # Return empty config if file doesn't exist
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {} # Return empty config on error

def save_config(config_data):
    """Saves the given configuration data to settings.json."""
    _ensure_config_dir_exists()
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4)

def load_openai_key():
    """Loads the OpenAI API key from the .env file at the project root."""
    load_dotenv(dotenv_path=ENV_PATH)
    return os.getenv("OPENAI_API_KEY")

def save_openai_key(api_key):
    """Saves or updates the OpenAI API key in the .env file at the project root."""
    # This creates the .env file if it doesn't exist.
    set_key(dotenv_path=ENV_PATH, key_to_set="OPENAI_API_KEY", value_to_set=api_key)

def load_gemini_key():
    """Loads the Gemini API key from the .env file at the project root."""
    load_dotenv(dotenv_path=ENV_PATH)
    return os.getenv("GEMINI_API_KEY")

def save_gemini_key(api_key):
    """Saves or updates the Gemini API key in the .env file at the project root."""
    # This creates the .env file if it doesn't exist.
    set_key(dotenv_path=ENV_PATH, key_to_set="GEMINI_API_KEY", value_to_set=api_key)