from enum import Enum, auto
import os
import logging

from . import utils
LOG_FILE = os.path.join(utils.get_log_dir(), "subscription.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    """Defines the available subscription tiers."""
    FREE = "Free"
    CREATOR = "Creator"
    ARCHITECT = "Architect"
    VISIONARY = "Visionary"

    @classmethod
    def get_tier_names(cls):
        """Returns a list of all tier names."""
        return [tier.value for tier in cls]

# Defines the hierarchical order of tiers for feature inheritance.
TIER_HIERARCHY = [
    SubscriptionTier.FREE,
    SubscriptionTier.CREATOR,
    SubscriptionTier.ARCHITECT,
    SubscriptionTier.VISIONARY,
]

class Feature(Enum):
    """Defines specific features that can be locked by tier."""
    AI_SUGGESTION = auto()
    APPLY_AI_EDIT = auto()
    FULL_REFACTOR = auto()
    AUTO_TASK_PLANNING = auto()
    AI_SESSION_SUMMARY = auto()

# Defines only the *new* features unlocked at each tier.
# Higher tiers automatically inherit features from lower tiers.
TIER_FEATURES = {
    SubscriptionTier.FREE: set(),
    SubscriptionTier.CREATOR: {Feature.AI_SUGGESTION, Feature.APPLY_AI_EDIT},
    SubscriptionTier.ARCHITECT: {Feature.FULL_REFACTOR, Feature.AI_SESSION_SUMMARY},
    SubscriptionTier.VISIONARY: {Feature.AUTO_TASK_PLANNING},
}

def is_feature_enabled(tier: SubscriptionTier, feature: Feature) -> bool:
    """
    Checks if a feature is enabled for a given subscription tier.
    Higher tiers inherit all features from lower tiers.
    """
    logger.debug(f"Checking if feature '{feature.name}' is enabled for tier '{tier.value}'.")
    try:
        current_tier_index = TIER_HIERARCHY.index(tier)
    except ValueError:
        logger.error(f"Invalid tier '{tier}' passed to is_feature_enabled.")
        return False # Should not happen with valid enum

    # Check the user's tier and all tiers below it in the hierarchy.
    for i in range(current_tier_index + 1):
        lower_tier = TIER_HIERARCHY[i]
        if feature in TIER_FEATURES.get(lower_tier, set()):
            logger.debug(f"Feature '{feature.name}' is ENABLED for tier '{tier.value}'.")
            return True
    logger.debug(f"Feature '{feature.name}' is DISABLED for tier '{tier.value}'.")
    return False

def get_tier_by_name(tier_name: str) -> SubscriptionTier:
    """Gets the enum member from a string name, defaulting to Free."""
    for tier in SubscriptionTier:
        if tier.value == tier_name:
            return tier
    logger.warning(f"Tier name '{tier_name}' not found. Defaulting to FREE tier.")
    return SubscriptionTier.FREE