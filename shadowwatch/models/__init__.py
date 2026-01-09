"""Shadow Watch database models (SQLAlchemy)"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

# Create a base class for Shadow Watch models
# Users can integrate this with their existing Base if needed
Base = declarative_base()


class UserActivityEvent(Base):
    """
    Raw activity events (audit trail)
    
    Tracks every user interaction:
    - view: Viewing an asset
    - search: Searching for symbols
    - trade: Executing trades
    - watchlist_add: Adding to watchlist
    - alert_set: Setting price alerts
    """
    __tablename__ = "shadow_watch_activity_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(String(20), default="stock")
    action_type = Column(String(20), nullable=False)
    event_metadata = Column(JSON, default=dict)
    occurred_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class UserInterest(Base):
    """
    Aggregated interest scores
    
    Represents user's interest in specific assets based on activity
    """
    __tablename__ = "shadow_watch_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(String(20), default="stock")
    score = Column(Float, default=0.0)
    activity_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    portfolio_value = Column(Float, nullable=True)
    first_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_interaction = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LibraryVersion(Base):
    """
    Library snapshots (versioning)
    
    Stores historical versions of user's library for auditing
    """
    __tablename__ = "shadow_watch_library_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    version = Column(Integer, nullable=False)
    fingerprint = Column(String(64), nullable=False, index=True)
    snapshot_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
