"""
Shadow Watch - Main API

This is the primary interface users interact with.
All database sessions and configurations are injected.
"""

from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from shadowwatch.utils.cache import create_cache, CacheBackend
from shadowwatch.core.tracker import track_activity
from shadowwatch.core.scorer import generate_library_snapshot
from shadowwatch.core.fingerprint import verify_fingerprint
from shadowwatch.core.trust_score import calculate_trust_score
from shadowwatch.models import Base  # For init_database()


class ShadowWatch:
    """
    Shadow Watch behavioral intelligence system

    Fully free and open source. All features available with no license required.

    Features:
    - track()                  - Track user activity silently
    - get_profile()            - Get user behavioral profile
    - get_library()            - Get interest library
    - verify_login()           - Calculate trust score for logins
    - calculate_continuity()   - Temporal actor persistence (ATO detection)
    - detect_divergence()      - Behavioral divergence detection
    - pre_auth_intent()        - Pre-auth intent analysis

    Args:
        database_url: SQLAlchemy async database URL (e.g., "postgresql+asyncpg://...")
        redis_url: Optional Redis URL for shared caching (recommended for production)
                  Example: "redis://localhost:6379"
                  If None, uses in-memory cache (single-instance only)

    ⚠️ IMPORTANT: For multi-instance deployments, MUST provide redis_url!
    Without Redis, each instance will have separate cache → data inconsistency.
    """

    def __init__(
        self,
        database_url: str,
        redis_url: Optional[str] = None
    ):
        """
        Shadow Watch - Behavioral Intelligence Library

        Args:
            database_url: SQLAlchemy async database URL (e.g., "postgresql+asyncpg://...")
            redis_url: Optional Redis URL for shared caching

        Examples:
            sw = ShadowWatch(database_url="postgresql+asyncpg://user:pass@host/db")
            await sw.track(user_id=123, entity_id="AAPL", action="view")

            profile = await sw.get_profile(user_id=123)
            continuity = await sw.calculate_continuity("user_123")
        """
        self.database_url = database_url

        # Enforce PostgreSQL requirement
        if "postgresql" not in database_url.lower() and "postgres" not in database_url.lower():
            raise ValueError(
                "Shadow Watch requires PostgreSQL.\n\n"
                "SQLite is not supported due to incompatible features (TIMESTAMPTZ, JSONB, triggers).\n\n"
                "Use PostgreSQL or managed services like Supabase:\n"
                "  database_url='postgresql+asyncpg://user:pass@host:5432/dbname'\n\n"
                "For local development, use Docker:\n"
                "  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15"
            )

        # Create async engine with proper connection args
        connect_args = {}
        clean_url = database_url

        if "postgresql" in database_url.lower() or "postgres" in database_url.lower():
            # asyncpg doesn't accept sslmode as URL parameter
            if "?" in database_url:
                clean_url = database_url.split("?")[0]

        self.engine = create_async_engine(clean_url, echo=False, connect_args=connect_args)
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Shared cache (Redis for production, Memory for dev)
        self.cache: CacheBackend = create_cache(redis_url)

        # Initialize all features (no license gates)
        self._init_core()

    def _init_core(self):
        """Initialize all Shadow Watch features"""
        from shadowwatch.core.tracking import TrackingEngine
        from shadowwatch.core.library import LibraryEngine
        from shadowwatch.core.profile import ProfileEngine

        self.tracking = TrackingEngine(self.AsyncSessionLocal)
        self.library = LibraryEngine(self.AsyncSessionLocal)
        self.profile = ProfileEngine(self.library)

        print("✅ Shadow Watch initialized")

    async def init_database(self):
        """
        Initialize database tables

        Creates all required Shadow Watch tables. Call this once during setup.

        Example:
            sw = ShadowWatch(...)
            await sw.init_database()
        """
        # CRITICAL: Import all models to register them with Base.metadata
        from shadowwatch.models.interest import UserInterest
        from shadowwatch.models.activity import UserActivityEvent
        from shadowwatch.models.library import LibraryVersion

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # ===== PUBLIC API =====

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

        Examples:
            await sw.track(user_id=123, entity_id="AAPL", action="view")
            await sw.track(
                user_id=123,
                entity_id="AAPL",
                action="trade",
                metadata={"shares": 10, "price": 150.00}
            )
        """
        return await self.tracking.track(user_id, entity_id, action, metadata)

    async def get_profile(self, user_id: int) -> Dict:
        """
        Get user's behavioral profile

        Args:
            user_id: User identifier

        Returns:
            {
                "user_id": int,
                "total_items": int,
                "fingerprint": str,
                "library": [...],
                "pinned_count": int
            }
        """
        return await self.profile.get(user_id)

    async def get_library(self, user_id: int, limit: int = 15) -> Dict:
        """
        Get user's interest library

        Alias for get_profile().

        Args:
            user_id: User identifier
            limit: Maximum number of items

        Returns:
            Same as get_profile()
        """
        return await self.library.get(user_id, limit)

    async def verify_login(
        self,
        user_id: int,
        request_context: Dict
    ) -> Dict:
        """
        Calculate trust score for login / sensitive action

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
        async with self.AsyncSessionLocal() as db:
            return await calculate_trust_score(db, user_id, request_context)

    async def calculate_continuity(
        self,
        subject_id: str,
        context: Optional[Dict] = None
    ):
        """
        Calculate temporal actor persistence

        Measures whether the current actor controlling an account
        remains coherent with the account's historical behavior.
        Core signal for Account Takeover (ATO) detection.

        Args:
            subject_id: Subject identifier (user_id, account_id, etc.)
            context: Optional context (IP, device, location)

        Returns:
            {
                "score": float (0.0-1.0),
                "confidence": float (0.0-1.0),
                "half_life": float (seconds),
                "state": "learning" | "stable" | "drifting" | "diverging"
            }
        """
        from shadowwatch.invariant.integration import calculate_continuity_impl

        async with self.AsyncSessionLocal() as db:
            return await calculate_continuity_impl(db, subject_id, context)

    async def detect_divergence(
        self,
        subject_id: str,
        window: Optional[int] = None
    ):
        """
        Detect behavioral divergence

        Detects when behavioral evolution stops being self-consistent
        and starts being adversarial.

        Args:
            subject_id: Subject identifier
            window: Time window in hours (default: 24)

        Returns:
            {
                "magnitude": float (0.0-1.0),
                "velocity": float,
                "mode": "shock" | "creep" | "fracture" | "none",
                "confidence": float (0.0-1.0)
            }
        """
        raise NotImplementedError(
            "detect_divergence() is coming soon. "
            "Track progress at https://github.com/Tanishq1030/shadow-watch"
        )

    async def pre_auth_intent(
        self,
        identifier: str,
        observations: Dict
    ):
        """
        Analyze pre-authentication intent

        Analyzes behavioral signals before authentication to detect
        credential stuffing and other pre-auth attacks.

        Args:
            identifier: Email, username, or device_id
            observations: {
                "navigation_path": List[str],
                "time_to_submit": float,
                "retry_count": int
            }

        Returns:
            {
                "intent_score": float (0.0-1.0),
                "confidence": float (0.0-1.0),
                "applicable": bool
            }
        """
        raise NotImplementedError(
            "pre_auth_intent() is coming soon. "
            "Track progress at https://github.com/Tanishq1030/shadow-watch"
        )
