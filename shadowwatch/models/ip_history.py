"""
UserIPHistory Model

Tracks known IPs per user for IP-based trust scoring.
A new IP from an unknown country is far more suspicious than
a new IP from the user's usual country.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from datetime import datetime, timezone

from shadowwatch.models import Base


class UserIPHistory(Base):
    """
    Known IP registry per user.

    One row per unique (user_id, ip_address). Updated on each login.

    Trust heuristics applied by trust_score.py:
        - Known IP, previously trusted    → 1.0
        - New IP, same country as history → 0.65
        - New IP, new country             → 0.4
        - No IP history at all            → 0.7 (first-ever login)
    """

    __tablename__ = "shadow_watch_ip_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    ip_address = Column(String(45), nullable=False, index=True)  # IPv4 or IPv6
    country = Column(String(2), nullable=True)   # ISO 3166-1 alpha-2 ("US", "IN")
    asn = Column(String(20), nullable=True)       # Autonomous System Number

    first_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # How many times this IP has been seen for this user
    seen_count = Column(Integer, default=1, nullable=False)

    # Explicitly trusted flag (set when user confirms a suspicious login)
    is_trusted = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        # Fast lookup: is this (user, IP) known?
        Index("idx_ip_user_address", "user_id", "ip_address"),
        # For "what country does this user usually login from?"
        Index("idx_ip_user_country", "user_id", "country"),
    )
