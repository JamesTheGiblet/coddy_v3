import hashlib
import os
import logging

# Set up logging
LOG_DIR = r"C:\Users\gilbe\Documents\GitHub\coddy_v3\coddy_core\log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "security.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def hash_password(password: str, salt: bytes) -> str:
    """Hashes a password with a given salt using PBKDF2."""
    try:
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # Recommended number of iterations
        )
        logger.debug("Password hashed successfully.")
        return pwd_hash.hex()
    except Exception:
        logger.exception("An error occurred during password hashing.")
        raise

def verify_password(stored_hash: str, salt_hex: str, provided_password: str) -> bool:
    """Verifies a provided password against a stored hash and salt."""
    try:
        salt = bytes.fromhex(salt_hex)
        # Use the same hash_password function to ensure the algorithm matches
        return stored_hash == hash_password(provided_password, salt)
    except Exception:
        logger.exception("An error occurred during password verification.")
        raise