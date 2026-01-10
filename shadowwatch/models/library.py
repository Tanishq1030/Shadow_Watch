"""
Shadow Watch Library Versions Model

Stores point-in-time snapshots of user libraries for versioning and fingerprinting
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class LibraryVersion(Base):
    """
    Library snapshots (versioning)
    
    Stores historical versions of user's library for auditing and recovery.
    Each snapshot includes the behavioral fingerprint for that point in time.
    
    Responsibility:
    - Store library snapshots
    - Track fingerprint evolution
    - Enable rollback/undo
    - Support behavioral drift detection
    
    Usage:
    - Created when generate_library_snapshot() is called
    - Used for fingerprint verification during login
    - Enables 48-hour undo window for pruned items
    """
    __tablename__ = "shadow_watch_library_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    version = Column(Integer, nullable=False)
    fingerprint = Column(String(64), nullable=False, index=True)  # SHA256 hash
    snapshot_data = Column(JSON, nullable=False)  # Full library data
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
