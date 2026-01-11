"""
Input Validators

Validates user inputs for Shadow Watch to prevent errors and security issues.
Designed to be flexible - accepts custom actions for any industry.
"""

from typing import Dict, Optional
import warnings
import json

# Standard action types (recommended, but not enforced)
STANDARD_ACTIONS = {
    "view": 1,        # Viewing an asset/product/post
    "search": 3,      # Searching for items
    "alert": 5,       # Setting alerts/notifications
    "watchlist": 8,   # Adding to favorites/watchlist
    "trade": 10,      # High-value actions (trades, purchases)
}

# Deprecated action names (for backwards compatibility)
DEPRECATED_ACTIONS = {
    "alert_set": "alert",
    "watchlist_add": "watchlist",
}


def validate_action(action: str, strict: bool = False) -> str:
    """
    Validate action type
    
    Args:
        action: Action string to validate
        strict: If True, only allow standard actions (default: False)
    
    Returns:
        Validated action string (lowercased)
    
    Raises:
        ValueError: If action is invalid (empty or too long)
    
    Note:
        By default, accepts any non-empty action string to allow
        custom actions for different industries (e-commerce, gaming, SaaS, etc.)
        
        Standard actions: view, search, alert, watchlist, trade
        
    Examples:
        # Finance
        validate_action("trade")  # ✅ Returns: "trade"
        
        # E-commerce
        validate_action("add_to_cart")  # ✅ Returns: "add_to_cart"
        
        # Social media
        validate_action("like")  # ✅ Returns: "like"
        
        # Gaming
        validate_action("equip")  # ✅ Returns: "equip"
    """
    if not isinstance(action, str):
        raise ValueError(f"action must be a string, got {type(action).__name__}")
    
    action = action.strip().lower()
    
    if not action:
        raise ValueError("action cannot be empty")
    
    if len(action) > 50:
        raise ValueError(f"action too long (max 50 chars), got {len(action)}")
    
    # Check for deprecated actions
    if action in DEPRECATED_ACTIONS:
        recommended = DEPRECATED_ACTIONS[action]
        warnings.warn(
            f"Action '{action}' is deprecated. Use '{recommended}' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        action = recommended
    
    # Strict mode: only allow standard actions
    if strict and action not in STANDARD_ACTIONS:
        raise ValueError(
            f"Invalid action '{action}'. "
            f"Allowed actions: {', '.join(STANDARD_ACTIONS.keys())}"
        )
    
    return action


def get_action_weight(action: str) -> int:
    """
    Get weight for an action
    
    Args:
        action: Action name
    
    Returns:
        Weight (1-10). Standard actions have predefined weights.
        Custom actions default to weight=1 (lowest priority).
    
    Examples:
        get_action_weight("trade")     # → 10 (highest)
        get_action_weight("view")      # → 1 (lowest)
        get_action_weight("purchase")  # → 1 (custom action, lowest)
    """
    return STANDARD_ACTIONS.get(action.lower(), 1)


def validate_user_id(user_id: int) -> int:
    """
    Validate user ID
    
    Args:
        user_id: User ID to validate
    
    Returns:
        Validated user ID
    
    Raises:
        ValueError: If user_id is invalid
    
    Responsibility:
        - Ensure user_id is positive integer
        - Prevent invalid queries
    """
    if not isinstance(user_id, int):
        raise ValueError(f"user_id must be an integer, got {type(user_id).__name__}")
    
    if user_id <= 0:
        raise ValueError(f"user_id must be positive, got {user_id}")
    
    return user_id


def validate_entity_id(entity_id: str) -> str:
    """
    Validate entity ID (symbol/ticker/product/post/etc.)
    
    Args:
        entity_id: Entity identifier to validate
    
    Returns:
        Validated entity ID (preserves case)
    
    Raises:
        ValueError: If entity_id is invalid
    
    Note:
        Does NOT force uppercase to support:
        - Crypto: "bitcoin", "ethereum" (lowercase by convention)
        - Custom IDs: "my-portfolio", "tech-sector"  
        - Product IDs: "product_12345"
        - Post IDs: "post_789"
        - International: Non-Latin characters
    
    Examples:
        # Finance (uppercase)
        validate_entity_id("AAPL")  # → "AAPL"
        
        # Crypto (lowercase)
        validate_entity_id("bitcoin")  # → "bitcoin"
        
        # E-commerce (mixed case)
        validate_entity_id("product_12345")  # → "product_12345"
        
        # Social media
        validate_entity_id("post_789")  # → "post_789"
    """
    if not isinstance(entity_id, str):
        raise ValueError(f"entity_id must be a string, got {type(entity_id).__name__}")
    
    entity_id = entity_id.strip()
    
    if not entity_id:
        raise ValueError("entity_id cannot be empty")
    
    if len(entity_id) > 100:  # Increased from 20 for flexibility
        raise ValueError(f"entity_id too long (max 100 chars), got {len(entity_id)}")
    
    # Preserve user's casing (don't force uppercase)
    return entity_id


def sanitize_metadata(metadata: Optional[Dict]) -> Dict:
    """
    Sanitize metadata dictionary
    
    Args:
        metadata: Metadata dict to sanitize
    
    Returns:
        Sanitized metadata dict (empty dict if None)
    
    Raises:
        ValueError: If metadata is invalid
    
    Note:
        Limit is 5000 chars JSON to allow rich metadata while
        preventing database bloat and abuse.
    """
    if metadata is None:
        return {}
    
    if not isinstance(metadata, dict):
        raise ValueError(f"metadata must be a dict, got {type(metadata).__name__}")
    
    # Limit metadata size (prevent abuse)
    metadata_json = json.dumps(metadata)
    if len(metadata_json) > 5000:  # Increased from 1000 for flexibility
        raise ValueError(
            f"metadata too large (max 5000 chars JSON), got {len(metadata_json)}"
        )
    
    return metadata
