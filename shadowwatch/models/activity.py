"""
Shadow Watch Activity Events Model

Tracks raw user activity events for behavioral analysis
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime, timezone

# Import shared Base from parent package
from shadowwatch.models import Base


class UserActivityEvent(Base):
    """
    Raw activity events (audit trail)
    
    Tracks every user interaction:
    - view: Viewing an asset
    - search: Searching for symbols
    - trade: Executing trades
    - watchlist_add: Adding to watchlist
    - alert_set: Setting price alerts
    
    Responsibility:
    - Store all raw user actions
    - Provide audit trail
    - Enable behavioral analysis
    """
    __tablename__ = "shadow_watch_activity_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(String(20), default="stock")
    action_type = Column(String(20), nullable=False)
    event_metadata = Column(JSON, default=dict)
    occurred_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
