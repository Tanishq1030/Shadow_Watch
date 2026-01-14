"""
Library Engine - FREE TIER

Handles interest library generation and retrieval.
"""
from typing import Dict
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shadowwatch.models import UserInterest
import hashlib

MAX_LIBRARY_SIZE = 50
PINNED_PRIORITY_WEIGHT = 100.0


class LibraryEngine:
    """
    Interest library engine - FREE TIER
    
    Responsibilities:
    - Generate curated library
    - Apply scoring algorithm
    - Return top entities
    
    No license required. This is a core free tier feature.
    """
    
    def __init__(self, async_session_local):
        """
        Initialize library engine
        
        Args:
            async_session_local: SQLAlchemy async session factory
        """
        self.async_session_local = async_session_local
    
    async def get(
        self,
        user_id: int,
        limit: int = 15
    ) -> Dict:
        """
        Get user's curated interest library
        
        Args:
            user_id: User identifier
            limit: Maximum entries to return (ignored, returns top 50)
        
        Returns:
            {
                "version": int,
                "generated_at": str,
                "total_items": int,
                "pinned_count": int,
                "fingerprint": str,
                "library": List[Dict]
            }
        """
        async with self.async_session_local() as db:
            return await self._generate_library_snapshot(db, user_id)
    
    async def _generate_library_snapshot(self, db: AsyncSession, user_id: int) -> dict:
        """
        Generate current Shadow Watch library + fingerprint
        
        Internal implementation.
        """
        # Fetch all interests
        result = await db.execute(
            select(UserInterest).where(UserInterest.user_id == user_id)
        )
        interests = result.scalars().all()

        if not interests:
            return {
                "version": 1,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_items": 0,
                "pinned_count": 0,
                "fingerprint": hashlib.sha256(b"empty_library").hexdigest(),
                "library": []
            }

        # Apply pinning boost for ranking
        ranked = []
        for item in interests:
            effective_score = item.score
            if item.is_pinned:
                effective_score += PINNED_PRIORITY_WEIGHT
            
            ranked.append({
                "symbol": item.symbol,
                "asset_type": item.asset_type,
                "score": item.score,
                "effective_score": effective_score,
                "is_pinned": item.is_pinned,
                "last_interaction": item.last_interaction,
                "activity_count": item.activity_count
            })

        # Sort by effective score
        ranked.sort(key=lambda x: x["effective_score"], reverse=True)

        # Build tiered library (top 50)
        library_items = []
        pinned_count = 0
        
        for i, item in enumerate(ranked[:MAX_LIBRARY_SIZE]):
            tier = 1 if item["is_pinned"] else (2 if i < 30 else 3)
            
            library_items.append({
                "symbol": item["symbol"],
                "asset_type": item["asset_type"],
                "score": round(item["score"], 3),
                "tier": tier,
                "rank": i + 1,
                "is_pinned": item["is_pinned"],
                "last_interaction": item["last_interaction"].isoformat() if item["last_interaction"] else None
            })
            
            if item["is_pinned"]:
                pinned_count += 1

        # Generate stable fingerprint
        top_symbols = [item["symbol"] for item in library_items[:10]]
        sectors = list({item["asset_type"] for item in library_items})
        intensity = "high" if len(library_items) > 30 else "medium" if len(library_items) > 10 else "low"
        
        fingerprint_input = f"""
PINNED:{pinned_count}
TOP:{''.join(sorted(top_symbols))}
SECTORS:{''.join(sorted(sectors))}
INTENSITY:{intensity}
SIZE:{len(library_items)}
"""
        fingerprint = hashlib.sha256(fingerprint_input.strip().encode()).hexdigest()

        return {
            "version": len(library_items) + 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(library_items),
            "pinned_count": pinned_count,
            "fingerprint": fingerprint,
            "library": library_items
        }
