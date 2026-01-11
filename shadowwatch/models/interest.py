"""
Shadow Watch User Interests Model

Stores aggregated interest scores based on user activity
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime, timezone

# Import shared Base from parent package
from shadowwatch.models import Base


class UserInterest(Base):
    """
    Aggregated interest scores
    
    Represents user's interest in specific assets based on activity.
    Scores range from 0.0 to 1.0, with higher scores indicating stronger interest.
    
    Responsibility:
    - Store calculated interest scores
    - Track pinned status (for portfolio holdings)
    - Enable quick profile generation
    - Support smart pruning decisions
    
    Scoring:
    - Updated when track_activity() is called
    - Weighted by action type (view=1, trade=10)
    - Capped at 1.0
    - Decays over time if inactive (optional)
    """
    __tablename__ = "shadow_watch_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(String(20), default="stock")
    score = Column(Float, default=0.0)
    activity_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)  # Auto-pinned for trades
    portfolio_value = Column(Float, nullable=True)  # Investment amount
    first_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_interaction = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
