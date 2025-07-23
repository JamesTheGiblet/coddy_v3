import json
import os
import logging

# NOTE: This manager uses the python-dotenv library.
# Ensure it is installed: pip install python-dotenv
from dotenv import load_dotenv, set_key

CONFIG_DIR = ".coddy"
CONFIG_FILE = "settings.json"

# Set up logging
LOG_DIR = r"C:\Users\gilbe\Documents\GitHub\coddy_v3\coddy_core\log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "config_manager.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

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
        logger.info("Settings file not found, returning empty config.")
        return {}  # Return empty config if file doesn't exist
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info("Configuration loaded successfully from %s.", CONFIG_PATH)
            return config
    except (json.JSONDecodeError, IOError) as e:
        logger.exception("Failed to load or parse config file %s.", CONFIG_PATH)
        return {} # Return empty config on error

def save_config(config_data):
    """Saves the given configuration data to settings.json."""
    _ensure_config_dir_exists()
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        logger.info("Configuration saved successfully to %s.", CONFIG_PATH)
    except IOError as e:
        logger.exception("Failed to save config file %s.", CONFIG_PATH)

def load_openai_key():
    """Loads the OpenAI API key from the .env file at the project root."""
    load_dotenv(dotenv_path=ENV_PATH)
    key = os.getenv("OPENAI_API_KEY")
    if key:
        logger.info("OpenAI API key loaded from .env.")
    else:
        logger.warning("OpenAI API key not found in .env.")
    return key

def save_openai_key(api_key):
    """Saves or updates the OpenAI API key in the .env file at the project root."""
    try:
        # This creates the .env file if it doesn't exist.
        set_key(dotenv_path=ENV_PATH, key_to_set="OPENAI_API_KEY", value_to_set=api_key)
        logger.info("OpenAI API key saved to .env.")
    except IOError as e:
        logger.exception("Failed to save OpenAI API key to .env file.")

def load_gemini_key():
    """Loads the Gemini API key from the .env file at the project root."""
    load_dotenv(dotenv_path=ENV_PATH)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        logger.info("Gemini API key loaded from .env.")
    else:
        logger.warning("Gemini API key not found in .env.")
    return key

def save_gemini_key(api_key):
    """Saves or updates the Gemini API key in the .env file at the project root."""
    try:
        # This creates the .env file if it doesn't exist.
        set_key(dotenv_path=ENV_PATH, key_to_set="GEMINI_API_KEY", value_to_set=api_key)
        logger.info("Gemini API key saved to .env.")
    except IOError as e:
        logger.exception("Failed to save Gemini API key to .env file.")