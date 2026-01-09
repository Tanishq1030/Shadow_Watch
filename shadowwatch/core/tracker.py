"""
Activity Tracking Core Module

Tracks user interactions silently for behavioral profiling
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shadowwatch.models import UserActivityEvent, UserInterest
from typing import Literal

ActivityAction = Literal["view", "trade", "watchlist_add", "alert_set", "search"]

# Action weights for scoring
ACTION_WEIGHTS = {
    "view": 1,
    "search": 3,
    "trade": 10,
    "alert_set": 5,
    "watchlist_add": 8,
}


async def track_activity(
    db: AsyncSession,
    user_id: int,
    symbol: str,
    action: ActivityAction,
    event_metadata: dict | None = None
):
    """
    Track user activity silently for Shadow Watch library
    
    Args:
        db: Database session (injected by caller)
        user_id: User identifier
        symbol: Asset symbol (e.g., "AAPL")
        action: Action type ("view", "trade", "search", etc.)
        event_metadata: Optional additional context
    
    Implementation: Week 1 Complete ✅
    
    This runs SILENTLY - no user-visible effects
    Updates happen asynchronously
    """
    symbol_upper = symbol.upper()
    
    # 1. Record raw activity event (audit trail)
    event = UserActivityEvent(
        user_id=user_id,
        symbol=symbol_upper,
        asset_type="stock",
        action_type=action,
        event_metadata=event_metadata or {},
        occurred_at=datetime.now(timezone.utc)
    )
    db.add(event)
    
    # 2. Update or create aggregated interest score
    stmt = select(UserInterest).where(
        UserInterest.user_id == user_id,
        UserInterest.symbol == symbol_upper
    )
    result = await db.execute(stmt)
    interest = result.scalar_one_or_none()
    
    if not interest:
        # Create new interest
        interest = UserInterest(
            user_id=user_id,
            symbol=symbol_upper,
            score=0.0,
            activity_count=0,
            first_seen=datetime.now(timezone.utc),
            last_interaction=datetime.now(timezone.utc)
        )
        db.add(interest)
    
    # 3. Update score using weighted activity
    weight = ACTION_WEIGHTS.get(action, 1)
    interest.activity_count += 1
    interest.score = min(1.0, interest.score + (weight * 0.05))
    interest.last_interaction = datetime.now(timezone.utc)
    
    # 4. Auto-pin if action is "trade" (investment-based)
    if action == "trade" and event_metadata and event_metadata.get("portfolio_value"):
        interest.is_pinned = True
        interest.portfolio_value = event_metadata["portfolio_value"]
    
    await db.commit()
