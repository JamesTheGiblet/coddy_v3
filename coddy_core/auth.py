import dataclasses
import os
import logging
from . import subscription
from . import database, security, utils

LOG_FILE = os.path.join(utils.get_log_dir(), "auth.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@dataclasses.dataclass
class User:
    """Represents a logged-in user."""
    email: str
    tier: subscription.SubscriptionTier

def login(email, password) -> User | None:
    """
    Logs a user in by verifying their credentials against the database.
    """
    logger.info(f"Login attempt for: {email}")
    try:
        user_data = database.get_user_by_email(email.lower())
        if user_data and security.verify_password(user_data['password_hash'], user_data['salt'], password):
            tier = subscription.get_tier_by_name(user_data['tier'])
            logger.info(f"Login successful for: {email}")
            return User(email=user_data['email'], tier=tier)
        
        logger.warning(f"Login failed for {email}: Invalid credentials.")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during login for {email}")
        raise

def signup(email, password) -> User | None:
    """
    Signs up a new user, hashes their password, and stores them in the database.
    """
    logger.info(f"Signup attempt for: {email}")
    try:
        if database.get_user_by_email(email.lower()):
            logger.warning(f"Signup failed for {email}: User already exists.")
            return None # User already exists

        salt = os.urandom(16)
        password_hash = security.hash_password(password, salt)
        default_tier = subscription.SubscriptionTier.FREE.value

        success = database.add_user(email.lower(), password_hash, salt.hex(), default_tier)

        if success:
            logger.info(f"Signup successful for: {email}")
            # Return a dummy user object to signal success to the UI.
            # The user will still need to log in.
            return User(email=email.lower(), tier=subscription.SubscriptionTier.FREE)
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during signup for {email}")
        raise