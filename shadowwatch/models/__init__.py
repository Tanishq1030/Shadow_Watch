"""
Shadow Watch Database Models

Provides SQLAlchemy models for Shadow Watch data storage.

Models:
- UserActivityEvent: Raw activity events (audit trail)
- UserInterest: Aggregated interest scores
- LibraryVersion: Library snapshots for versioning

Usage:
    from shadowwatch.models import UserActivityEvent, UserInterest, LibraryVersion, Base
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
"""

from sqlalchemy.orm import declarative_base

# CRITICAL: Single shared Base for ALL models
# This ensures all tables use the same metadata object
Base = declarative_base()

# Import models AFTER Base is defined so they can use it
from shadowwatch.models.activity import UserActivityEvent
from shadowwatch.models.interest import UserInterest
from shadowwatch.models.library import LibraryVersion
from shadowwatch.models.device import UserDeviceHistory
from shadowwatch.models.ip_history import UserIPHistory
from shadowwatch.models.pre_auth import PreAuthSession
from shadowwatch.models.heatmap import UserActivityHeatmap

__all__ = [
    "UserActivityEvent",
    "UserInterest",
    "LibraryVersion",
    "UserDeviceHistory",
    "UserIPHistory",
    "PreAuthSession",
    "UserActivityHeatmap",
    "Base",
]
