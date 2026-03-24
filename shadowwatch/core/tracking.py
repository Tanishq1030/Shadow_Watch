"""
Tracking Engine - FREE TIER

Handles activity ingestion and storage.
"""
from typing import Dict, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shadowwatch.models import UserActivityEvent, UserInterest

# Actions are intentionally open-ended to stay domain agnostic
ActivityAction = str

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
            metadata: Optional additional context (e.g., {"asset_type": "article"})
        
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
        # 1. Record raw activity event (audit trail)
        metadata_dict = event_metadata or {}
        asset_type = metadata_dict.get("asset_type", "generic")
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
            # Update asset classification if provided
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
        
        # 5. Update Activity Heatmap (for temporal signals)
        from shadowwatch.models.heatmap import UserActivityHeatmap
        hour = datetime.now(timezone.utc).hour
        heatmap_stmt = select(UserActivityHeatmap).where(
            UserActivityHeatmap.user_id == user_id,
            UserActivityHeatmap.hour == hour
        )
        heatmap_res = await db.execute(heatmap_stmt)
        heatmap = heatmap_res.scalar_one_or_none()
        
        if heatmap:
            heatmap.weight += 1.0
        else:
            db.add(UserActivityHeatmap(user_id=user_id, hour=hour, weight=1.0))
            
        await db.commit()
