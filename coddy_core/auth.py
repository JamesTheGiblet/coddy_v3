import dataclasses
import subscription

@dataclasses.dataclass
class User:
    """Represents a logged-in user."""
    email: str
    tier: subscription.SubscriptionTier

# A dummy user database for local testing.
# In a real app, this would be a remote database.
DUMMY_USERS = {
    "free@coddy.ai": ("password", User(email="free@coddy.ai", tier=subscription.SubscriptionTier.FREE)),
    "creator@coddy.ai": ("password", User(email="creator@coddy.ai", tier=subscription.SubscriptionTier.CREATOR)),
    "architect@coddy.ai": ("password", User(email="architect@coddy.ai", tier=subscription.SubscriptionTier.ARCHITECT)),
    "visionary@coddy.ai": ("password", User(email="visionary@coddy.ai", tier=subscription.SubscriptionTier.VISIONARY)),
}

def login(email, password) -> User | None:
    """
    Dummy login function. Checks against a hardcoded dictionary.
    In a real app, this would make an API call to a Firebase/JWT backend.
    """
    user_data = DUMMY_USERS.get(email.lower())
    if user_data and user_data[0] == password:
        return user_data[1]
    return None

def signup(email, password) -> User | None:
    """
    Dummy signup function. Adds a user to the dictionary if not present.
    Defaults to a Free tier. Returns the new user on success, None if user exists.
    """
    if email.lower() in DUMMY_USERS:
        return None # User already exists
    
    new_user = User(email=email.lower(), tier=subscription.SubscriptionTier.FREE)
    DUMMY_USERS[email.lower()] = (password, new_user)
    return new_user