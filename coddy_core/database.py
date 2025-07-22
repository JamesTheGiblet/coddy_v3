import sqlite3
import os
from . import security
from . import subscription

DB_FILE = "coddy_users.db"
DB_PATH = os.path.join(".coddy", DB_FILE)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(".coddy", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the users table if it doesn't exist."""
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
        print("Empty database detected. Seeding with dummy users...")
        _seed_dummy_users(conn)

    conn.close()
    print("Database initialized.")

def _seed_dummy_users(conn):
    """Creates a dummy user for each subscription tier."""
    dummy_users = [
        ("free@coddy.ai", "password", subscription.SubscriptionTier.FREE),
        ("creator@coddy.ai", "password", subscription.SubscriptionTier.CREATOR),
        ("architect@coddy.ai", "password", subscription.SubscriptionTier.ARCHITECT),
        ("visionary@coddy.ai", "password", subscription.SubscriptionTier.VISIONARY),
    ]

    for email, password, tier in dummy_users:
        salt = os.urandom(16)
        password_hash = security.hash_password(password, salt)
        try:
            conn.execute(
                "INSERT INTO users (email, password_hash, salt, tier) VALUES (?, ?, ?, ?)",
                (email, password_hash, salt.hex(), tier.value),
            )
        except sqlite3.IntegrityError:
            # Should not happen on a fresh DB, but good practice
            print(f"User {email} already exists.")
    conn.commit()
    print(f"Seeded {len(dummy_users)} dummy users.")

def add_user(email, password_hash, salt, tier):
    """Adds a new user to the database."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (email, password_hash, salt, tier) VALUES (?, ?, ?, ?)",
            (email, password_hash, salt, tier),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False # This happens if the email is already in use
    finally:
        conn.close()
    return True

def get_user_by_email(email):
    """Retrieves a user's data from the database by their email."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user