"""
Shadow Watch - Main API

This is the primary interface users interact with.
All database sessions and configurations are injected.
"""

from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from shadowwatch.utils.license import verify_license_key
from shadowwatch.utils.cache import create_cache, CacheBackend
from shadowwatch.core.tracker import track_activity
from shadowwatch.core.scorer import generate_library_snapshot
from shadowwatch.core.fingerprint import verify_fingerprint
from shadowwatch.core.trust_score import calculate_trust_score
from shadowwatch.models import Base  # For init_database()


class ShadowWatch:
    """
    Shadow Watch behavioral intelligence system
    
    Args:
        database_url: SQLAlchemy async database URL (e.g., "postgresql+asyncpg://...")
        license_key: Your Shadow Watch license key (get trial at shadowwatch.dev)
        license_server_url: Optional custom license server URL
        redis_url: Optional Redis URL for shared caching (recommended for production)
                  Example: "redis://localhost:6379"
                  If None, uses in-memory cache (single-instance only)
    
    ⚠️ IMPORTANT: For multi-instance deployments, MUST provide redis_url!
    Without Redis, each instance will have separate cache → data inconsistency.
    """
    
    def __init__(
        self,
        database_url: str,
        license_key: Optional[str] = None,
        license_server_url: str = "https://shadow-watch-three.vercel.app",
        redis_url: Optional[str] = None
    ):
        self.database_url = database_url
        self.license_key = license_key
        self.license_server_url = license_server_url
        
        # Guardrail: Warn against SQLite async in production
        if "sqlite+aiosqlite" in database_url.lower():
            import warnings
            warnings.warn(
                "\n"
                "⚠️  SQLite async is supported for demos/testing only.\n"
                "   Schema propagation across async connections is unreliable.\n"
                "   For production, use PostgreSQL or MySQL.\n"
                "   See: https://github.com/Tanishq1030/Shadow_Watch#database-requirements",
                UserWarning,
                stacklevel=2
            )
        
        # Local dev mode (no license, 1000 events max)
        self._local_mode = (license_key is None)
        self._event_limit = 1000 if self._local_mode else None
        self._event_count = 0
        
        # Create async engine
        self.engine = create_async_engine(database_url, echo=False)
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Shared cache (Redis for production, Memory for dev)
        self.cache: CacheBackend = create_cache(redis_url)
        
        # Show local mode warning
        if self._local_mode:
            print("\n" + "="*70)
            print("⚠️  Shadow Watch: LOCAL DEV MODE (No License Required)")
            print("="*70)
            print("   • Limited to 1,000 events")
            print("   • For production, get free trial:")
            print("      https://shadow-watch-three.vercel.app/trial")
            print("="*70 + "\n")
        
        # Note: License verification now cached in Redis/Memory, not instance variable
    
    async def _ensure_license(self):
        """
        Verify license key (cached for 24 hours)
        
        Skips verification in local dev mode.
        Uses shared cache to avoid re-verification on every request
        across multiple instances.
        """
        # Skip license check in local dev mode
        if self._local_mode:
            if self._event_count >= self._event_limit:
                raise Exception(
                    f"\n❌ Local dev limit reached ({self._event_limit} events)\n"
                    f"   Get free trial: https://shadow-watch-three.vercel.app/trial\n"
                )
            self._event_count += 1
            return
        
        cache_key = f"shadowwatch:license:{self.license_key}"
        
        # Check cache first
        cached_license = await self.cache.get(cache_key)
        if cached_license:
            return  # Already verified
        
        # Verify with license server
        license_data = await verify_license_key(
            self.license_key,
            self.license_server_url
        )
        
        if not license_data["valid"]:
            raise Exception(f"Invalid license: {license_data.get('error', 'Unknown error')}")
        
        # Cache for 24 hours (86400 seconds)
        await self.cache.set(cache_key, license_data, ttl_seconds=86400)
        
        print(f"✅ Shadow Watch: Licensed to {license_data['customer']} ({license_data['tier']})")
    
    async def init_database(self):
        """
        Initialize database tables
        
        Creates all required Shadow Watch tables. Call this once during setup.
        
        Example:
            sw = ShadowWatch(...)
            await sw.init_database()
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def track(
        self,
        user_id: int,
        entity_id: str,
        action: str,
        metadata: Optional[Dict] = None
    ):
        """
        Track user activity silently
        
        Args:
            user_id: User identifier
            entity_id: Entity being interacted with (e.g., "AAPL", "product_123")
            action: Action type ("view", "trade", "search", "watchlist_add", "alert_set")
            metadata: Optional additional context
        """
        await self._ensure_license()
        
        async with self.AsyncSessionLocal() as db:
            await track_activity(
                db=db,
                user_id=user_id,
                symbol=entity_id,
                action=action,
                event_metadata=metadata
            )
    
    async def get_profile(self, user_id: int) -> Dict:
        """
        Get user's behavioral profile
        
        Returns:
            {
                "total_items": int,
                "fingerprint": str,
                "library": [...],
                "pinned_count": int
            }
        """
        await self._ensure_license()
        
        async with self.AsyncSessionLocal() as db:
            return await generate_library_snapshot(db, user_id)
    
    async def verify_login(
        self,
        user_id: int,
        request_context: Dict
    ) -> Dict:
        """
        Calculate trust score for login/sensitive action
        
        Args:
            request_context: {
                "ip": str,
                "country": Optional[str],
                "user_agent": str,
                "device_fingerprint": Optional[str],
                "library_fingerprint": Optional[str],
                "timestamp": Optional[datetime]
            }
        
        Returns:
            {
                "trust_score": float (0.0-1.0),
                "risk_level": str ("low", "medium", "elevated", "high"),
                "action": str ("allow", "monitor", "require_mfa", "block"),
                "factors": {...}
            }
        """
        await self._ensure_license()
        
        async with self.AsyncSessionLocal() as db:
            return await calculate_trust_score(db, user_id, request_context)
