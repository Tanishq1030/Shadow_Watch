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

from shadowwatch.models.activity import UserActivityEvent, Base as ActivityBase
from shadowwatch.models.interest import UserInterest
from shadowwatch.models.library import LibraryVersion

# Use the same Base for all models (from activity.py)
Base = ActivityBase

__all__ = [
    "UserActivityEvent",
    "UserInterest",
    "LibraryVersion",
    "Base"
]
