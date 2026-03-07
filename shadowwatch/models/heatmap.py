"""
User Activity Heatmap Model

Tracks frequency of activity per hour of day to build a behavioral time profile.
"""
from sqlalchemy import Column, Integer, Float, Index
from . import Base

class UserActivityHeatmap(Base):
    """
    Weight-based activity distribution over 24 hours.
    
    Fields:
        user_id: User identifier
        hour: Hour of day (0-23)
        weight: Cumulative activity weight or frequency count
    """
    __tablename__ = "shadow_watch_user_heatmaps"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True, nullable=False)
    hour = Column(Integer, nullable=False)
    weight = Column(Float, default=0.0)

    # Composite index for fast lookups
    __table_args__ = (
        Index('idx_user_hour', 'user_id', 'hour', unique=True),
    )

    def __repr__(self):
        return f"<UserActivityHeatmap(user_id={self.user_id}, hour={self.hour}, weight={self.weight})>"
