"""
Pre-Auth Session Model

Tracks transient signals from anonymous sessions before login.
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from . import Base
from datetime import datetime, timezone

class PreAuthSession(Base):
    """
    Anonymous session tracking for pre-authentication intent analysis.
    
    Fields:
        session_id: Unique identifier for the anonymous session (e.g. UUID)
        ip_address: Source IP
        device_fingerprint: Browser/device fingerprint
        signals: JSON blob of behavioral signals (typing cadence, mouse, features)
        created_at: When the session started
        updated_at: Last signal update
        associated_user_id: User assigned after successful login
    """
    __tablename__ = "shadow_watch_pre_auth_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128), index=True, unique=True, nullable=False)
    ip_address = Column(String(45), index=True)
    device_fingerprint = Column(String(128), index=True)
    signals = Column(JSON, default={})
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    associated_user_id = Column(Integer, index=True, nullable=True)

    def __repr__(self):
        return f"<PreAuthSession(session_id='{self.session_id}', ip='{self.ip_address}')>"
