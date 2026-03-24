"""
Activity Tracking Core Module

Tracks user interactions silently for behavioral profiling
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shadowwatch.models import UserActivityEvent, UserInterest

ActivityAction = str

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
        symbol: Entity identifier (e.g., "article-123" or "AAPL")
        action: Action type ("view", "purchase", "search", etc.)
        event_metadata: Optional additional context
    
    Implementation: Week 1 Complete ✅
    
    This runs SILENTLY - no user-visible effects
    Updates happen asynchronously
    """
    metadata_dict = event_metadata or {}
    asset_type = metadata_dict.get("asset_type", "generic")
    
    # 1. Record raw activity event (audit trail)
    event = UserActivityEvent(
        user_id=user_id,
        symbol=symbol,
        asset_type=asset_type,
        action_type=action,
        event_metadata=metadata_dict,
        occurred_at=datetime.now(timezone.utc)
    )
    db.add(event)
    
    # 2. Update or create aggregated interest score
    stmt = select(UserInterest).where(
        UserInterest.user_id == user_id,
        UserInterest.symbol == symbol
    )
    result = await db.execute(stmt)
    interest = result.scalar_one_or_none()
    
    if not interest:
        # Create new interest
        interest = UserInterest(
            user_id=user_id,
            symbol=symbol,
            score=0.0,
            activity_count=0,
            first_seen=datetime.now(timezone.utc),
            last_interaction=datetime.now(timezone.utc),
            asset_type=asset_type
        )
        db.add(interest)
    else:
        if "asset_type" in metadata_dict:
            interest.asset_type = asset_type
    
    # 3. Update score using weighted activity
    weight = ACTION_WEIGHTS.get(action, 1)
    interest.activity_count += 1
    interest.score = min(1.0, interest.score + (weight * 0.05))
    interest.last_interaction = datetime.now(timezone.utc)
    
    # 4. Auto-pin if explicitly requested or trade with investment metadata
    should_pin = False
    if metadata_dict.get("pin_interest") is True:
        should_pin = True
    elif action == "trade" and metadata_dict.get("portfolio_value"):
        should_pin = True
        interest.portfolio_value = metadata_dict["portfolio_value"]

    if should_pin:
        interest.is_pinned = True
    
    await db.commit()
