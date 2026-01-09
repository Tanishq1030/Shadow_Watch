"""
Smart Library Pruning

Removes lowest-activity items when library exceeds capacity
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from shadowwatch.models import UserInterest

MAX_LIBRARY_SIZE = 50


async def smart_prune_if_needed(db: AsyncSession, user_id: int) -> dict | None:
    """
    Remove lowest-activity item if library exceeds 50-item cap
    
    Args:
        db: Database session (injected by caller)
        user_id: User identifier
    
    Returns:
        {
            "removed_symbol": str,
            "reason": str,
            "days_inactive": int
        }
        or None if no pruning needed
    
    Implementation: Week 2 Complete ✅
    """
    # Count current items
    count_result = await db.execute(
        select(func.count()).select_from(UserInterest).where(UserInterest.user_id == user_id)
    )
    count = count_result.scalar()

    if count <= MAX_LIBRARY_SIZE:
        return None

    # Find removal candidate (lowest score, not pinned, oldest interaction)
    candidates = await db.execute(
        select(UserInterest)
        .where(
            and_(
                UserInterest.user_id == user_id,
                UserInterest.is_pinned == False
            )
        )
        .order_by(UserInterest.score.asc(), UserInterest.last_interaction.asc())
        .limit(1)
    )
    candidate = candidates.scalar_one_or_none()

    if not candidate:
        # All items are pinned, can't prune
        return None

    # Calculate inactivity
    days_inactive = (
        (datetime.now(timezone.utc) - candidate.last_interaction).days 
        if candidate.last_interaction else 999
    )
    
    removed_symbol = candidate.symbol
    
    # Delete the candidate
    await db.delete(candidate)
    await db.commit()
    
    return {
        "removed_symbol": removed_symbol,
        "reason": "low_activity",
        "days_inactive": days_inactive,
        "score": candidate.score
    }
