import hashlib
import os

def hash_password(password: str, salt: bytes) -> str:
    """Hashes a password with a given salt using PBKDF2."""
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Recommended number of iterations
    )
    return pwd_hash.hex()

def verify_password(stored_hash: str, salt_hex: str, provided_password: str) -> bool:
    """Verifies a provided password against a stored hash and salt."""
    salt = bytes.fromhex(salt_hex)
    # Use the same hash_password function to ensure the algorithm matches
    return stored_hash == hash_password(provided_password, salt)