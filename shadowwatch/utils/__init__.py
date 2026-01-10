"""Shadow Watch utilities"""

from shadowwatch.utils.license import verify_license_key, report_usage
from shadowwatch.utils.cache import create_cache, CacheBackend, RedisCache, MemoryCache
from shadowwatch.utils.validators import (
    validate_action,
    validate_user_id,
    validate_entity_id,
    sanitize_metadata,
    VALID_ACTIONS
)

__all__ = [
    # License
    "verify_license_key",
    "report_usage",
    # Cache
    "create_cache",
    "CacheBackend",
    "RedisCache",
    "MemoryCache",
    # Validators
    "validate_action",
    "validate_user_id",
    "validate_entity_id",
    "sanitize_metadata",
    "VALID_ACTIONS"
]
