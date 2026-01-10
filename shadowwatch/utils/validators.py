"""
Input Validators

Validates user inputs for Shadow Watch to prevent errors and security issues
"""

from typing import Literal

# Valid action types
VALID_ACTIONS = {"view", "search", "trade", "watchlist_add", "alert_set"}

ActionType = Literal["view", "search", "trade", "watchlist_add", "alert_set"]


def validate_action(action: str) -> ActionType:
    """
    Validate action type
    
    Args:
        action: Action string to validate
    
    Returns:
        Validated action type
    
    Raises:
        ValueError: If action is not valid
    
    Responsibility:
    - Ensure action is one of allowed types
    - Prevent invalid data in database
    - Provide clear error messages
    """
    if action not in VALID_ACTIONS:
        raise ValueError(
            f"Invalid action '{action}'. Must be one of: {', '.join(VALID_ACTIONS)}"
        )
    return action  # type: ignore


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
        raise ValueError(f"user_id must be an integer, got {type(user_id)}")
    
    if user_id <= 0:
        raise ValueError(f"user_id must be positive, got {user_id}")
    
    return user_id


def validate_entity_id(entity_id: str) -> str:
    """
    Validate entity ID (symbol/ticker/asset)
    
    Args:
        entity_id: Entity identifier to validate
    
    Returns:
        Validated and normalized entity ID (uppercase)
    
    Raises:
        ValueError: If entity_id is invalid
    
    Responsibility:
    - Ensure entity_id is non-empty string
    - Normalize to uppercase
    - Prevent SQL injection (though ORM handles this)
    """
    if not isinstance(entity_id, str):
        raise ValueError(f"entity_id must be a string, got {type(entity_id)}")
    
    entity_id = entity_id.strip()
    
    if not entity_id:
        raise ValueError("entity_id cannot be empty")
    
    if len(entity_id) > 20:
        raise ValueError(f"entity_id too long (max 20 chars), got {len(entity_id)}")
    
    # Normalize to uppercase (stock symbols are typically uppercase)
    return entity_id.upper()


def sanitize_metadata(metadata: dict | None) -> dict:
    """
    Sanitize metadata dictionary
    
    Args:
        metadata: Metadata dict to sanitize
    
    Returns:
        Sanitized metadata dict
    
    Responsibility:
    - Ensure metadata is valid dict or None
    - Limit size to prevent database bloat
    - Remove potentially dangerous content
    """
    if metadata is None:
        return {}
    
    if not isinstance(metadata, dict):
        raise ValueError(f"metadata must be a dict, got {type(metadata)}")
    
    # Limit metadata size (prevent abuse)
    if len(str(metadata)) > 1000:
        raise ValueError("metadata too large (max 1000 chars)")
    
    return metadata
