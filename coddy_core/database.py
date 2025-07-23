import sqlite3
import os
import logging
from . import security, subscription, utils

LOG_FILE = os.path.join(utils.get_log_dir(), "database.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DB_FILE = "coddy_users.db"
DB_PATH = os.path.join(utils.get_app_root(), ".coddy", DB_FILE)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the users table if it doesn't exist."""
    logger.info("Initializing database...")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                tier TEXT NOT NULL
            );
        """)
        conn.commit()

        # Seed database if empty
        cursor.execute("SELECT COUNT(id) FROM users")
        user_count = cursor.fetchone()[0]
        if user_count == 0:
            _seed_dummy_users(conn)
        
        logger.info("Database initialization complete.")
    except sqlite3.Error as e:
        logger.exception("A database error occurred during init_db.")
        raise # Re-raise to be caught by app.py for a fatal error message
    finally:
        if conn:
            conn.close()

def _seed_dummy_users(conn):
    """Creates a dummy user for each subscription tier."""
    logger.info("Empty database detected. Seeding with dummy users...")
    dummy_users = [
        ("free@coddy.ai", "password", subscription.SubscriptionTier.FREE),
        ("creator@coddy.ai", "password", subscription.SubscriptionTier.CREATOR),
        ("architect@coddy.ai", "password", subscription.SubscriptionTier.ARCHITECT),
        ("visionary@coddy.ai", "password", subscription.SubscriptionTier.VISIONARY),
    ]
    users_seeded = 0
    for email, password, tier in dummy_users:
        try:
            salt = os.urandom(16)
            password_hash = security.hash_password(password, salt)
            conn.execute(
                "INSERT INTO users (email, password_hash, salt, tier) VALUES (?, ?, ?, ?)",
                (email, password_hash, salt.hex(), tier.value),
            )
            users_seeded += 1
        except sqlite3.IntegrityError:
            logger.warning(f"User {email} already exists during seeding. Skipping.")
        except Exception:
            logger.exception(f"Failed to seed user {email}.")
    conn.commit()
    logger.info(f"Seeded {users_seeded} of {len(dummy_users)} dummy users.")

def add_user(email, password_hash, salt, tier):
    """Adds a new user to the database."""
    logger.info(f"Attempting to add user: {email}")
    conn = None
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (email, password_hash, salt, tier) VALUES (?, ?, ?, ?)",
            (email, password_hash, salt, tier),
        )
        conn.commit()
        logger.info(f"Successfully added user: {email}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Failed to add user {email}: email already exists.")
        return False # This happens if the email is already in use
    except Exception:
        logger.exception(f"An unexpected error occurred while adding user {email}.")
        return False
    finally:
        if conn:
            conn.close()

def get_user_by_email(email):
    """Retrieves a user's data from the database by their email."""
    logger.debug(f"Querying for user: {email}")
    conn = None
    try:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            logger.debug(f"Found user: {email}")
        else:
            logger.debug(f"User not found: {email}")
        return user
    except Exception:
        logger.exception(f"An error occurred while getting user {email}.")
        return None
    finally:
        if conn:
            conn.close()