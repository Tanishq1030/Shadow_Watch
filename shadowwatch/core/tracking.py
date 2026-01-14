"""
Tracking Engine - FREE TIER

Handles activity ingestion and storage.
"""
from typing import Dict, Optional, Literal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shadowwatch.models import UserActivityEvent, UserInterest

ActivityAction = Literal["view", "trade", "watchlist_add", "alert_set", "search"]

# Action weights for scoring
ACTION_WEIGHTS = {
    "view": 1,
    "search": 3,
    "trade": 10,
    "alert_set": 5,
    "watchlist_add": 8,
}


class TrackingEngine:
    """
    Activity tracking engine - FREE TIER
    
    Responsibilities:
    - Store activity events
    - Update interest scores
    - Maintain activity log
    
    No license required. This is a core free tier feature.
    """
    
    def __init__(self, async_session_local):
        """
        Initialize tracking engine
        
        Args:
            async_session_local: SQLAlchemy async session factory
        """
        self.async_session_local = async_session_local
    
    async def track(
        self,
        user_id: int,
        entity_id: str,
        action: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Track user activity
        
        Args:
            user_id: User identifier
            entity_id: Entity being interacted with
            action: Action type (view, search, like, etc.)
            metadata: Optional additional context
        
        Returns:
            {"tracked": True, "activity_id": int}
        """
        async with self.async_session_local() as db:
            await self._track_activity(
                db=db,
                user_id=user_id,
                symbol=entity_id,
                action=action,
                event_metadata=metadata
            )
        
        return {
            "tracked": True,
            "user_id": user_id,
            "entity_id": entity_id,
            "action": action
        }
    
    async def _track_activity(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str,
        action: str,
        event_metadata: dict | None = None
    ):
        """
        Internal tracking implementation
        
        This runs SILENTLY - no user-visible effects.
        Updates happen asynchronously.
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
