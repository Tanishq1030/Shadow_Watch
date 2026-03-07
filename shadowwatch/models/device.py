"""
UserDeviceHistory Model

Tracks known devices per user for device-based trust scoring.
Each unique (user_id, device_fingerprint) pair gets one row,
updated on every login from that device.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Index
from datetime import datetime, timezone

from shadowwatch.models import Base


class UserDeviceHistory(Base):
    """
    Known device registry per user.

    The device_fingerprint is supplied by the client (e.g. FingerprintJS,
    or a hash of User-Agent + screen dimensions + timezone). Shadow Watch
    does not generate it — it only stores and looks it up.

    trust_level:
        1.0  — explicitly trusted (user confirmed this device)
        0.8  — implicitly trusted (seen many times, no anomalies)
        0.5  — neutral (seen before but infrequently)
        0.3  — flagged (seen alongside anomalous continuity scores)
        0.0  — blocked
    """

    __tablename__ = "shadow_watch_device_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # Client-supplied device fingerprint (hash)
    device_fingerprint = Column(String(255), nullable=True, index=True)
    # Raw User-Agent string for reference
    user_agent = Column(String(512), nullable=True)

    first_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # How many times this device has been seen for this user
    seen_count = Column(Integer, default=1, nullable=False)

    # Computed trust level for this device (0.0–1.0)
    trust_level = Column(Float, default=0.8, nullable=False)

    __table_args__ = (
        # Fast lookup: is this (user, device) pair known?
        Index("idx_device_user_fingerprint", "user_id", "device_fingerprint"),
    )
