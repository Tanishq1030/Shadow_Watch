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
from shadowwatch.exceptions import LicenseError


class ShadowWatch:
    """
    Shadow Watch behavioral intelligence system
    
    Free Tier (no license needed):
    - track() - Track user activity
    - get_profile() - Get user profile
    - get_library() - Get interest library (alias for get_profile)
    
    Pro Tier (requires license_key):
    - calculate_continuity() - Temporal actor persistence
    - detect_divergence() - Behavioral divergence detection
    - pre_auth_intent() - Pre-auth intent analysis
    
    Args:
        database_url: SQLAlchemy async database URL (e.g., "postgresql+asyncpg://...")
        license_key: Optional Pro license key
        license_server_url: License server URL (for Pro tier)
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
        license_server_url: str = "https://shadow-watch-rust.vercel.app",
        redis_url: Optional[str] = None
    ):
        """
        Shadow Watch - Behavioral Intelligence Library
        
        Free Tier (no license needed):
        - track() - Track user activity
        - get_profile() - Get user profile
        - get_library() - Get interest library (alias for get_profile)
        
        Pro Tier (requires license_key):
        - calculate_continuity() - Temporal actor persistence
        - detect_divergence() - Behavioral divergence detection
        - pre_auth_intent() - Pre-auth intent analysis
        
        Args:
            database_url: SQLAlchemy async database URL (e.g., "postgresql+asyncpg://...")
            license_key: Optional Pro license key
            license_server_url: License server URL (for Pro tier)
            redis_url: Optional Redis URL for shared caching
        
        Examples:
            # Free tier (no license needed)
            sw = ShadowWatch(database_url="postgresql://localhost/db")
            await sw.track(user_id=123, entity_id="AAPL", action="view")
            
            # Pro tier (with license)
            sw = ShadowWatch(
                database_url="postgresql://localhost/db",
                license_key="SW-PRO-XXXX-XXXX-XXXX-XXXX"
            )
            continuity = await sw.calculate_continuity("user_123")
        """
        self.database_url = database_url
        self._license_key = license_key
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
        
        # FREE TIER SETUP (always available)
        self._init_free_tier()
        
        # PRO TIER SETUP (conditional)
        self._pro_enabled = False
        if license_key:
            # Note: Pro activation happens lazily on first Pro method call
            # This allows free tier to work even if Pro activation fails
            pass
    
    def _init_free_tier(self):
        """
        Initialize free tier features (always available)
        
        No license verification needed.
        Free tier has NO event limits.
        """
        from shadowwatch.core.tracking import TrackingEngine
        from shadowwatch.core.library import LibraryEngine
        from shadowwatch.core.profile import ProfileEngine
        
        # Initialize engines
        self.tracking = TrackingEngine(self.AsyncSessionLocal)
        self.library = LibraryEngine(self.AsyncSessionLocal)
        self.profile = ProfileEngine(self.library)
        
        print("✅ Shadow Watch Free Tier initialized")


    
    async def _ensure_license(self):
        """
        Verify license key (cached for 24 hours)
        
        Skips verification in local dev mode.
        Uses shared cache to avoid re-verification on every request
        across multiple instances.
        """
        # Skip if no license key (free tier)
        if not self._license_key:
            return
        
        cache_key = f"shadowwatch:license:{self._license_key}"
        
        # Check cache first
        cached_license = await self.cache.get(cache_key)
        if cached_license:
            return  # Already verified
        
        # Verify with license server
        license_data = await verify_license_key(
            self._license_key,
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
        # CRITICAL: Import all models to register them with Base.metadata
        # Each model must be imported before create_all() is called
        from shadowwatch.models.interest import UserInterest
        from shadowwatch.models.activity import UserActivityEvent
        from shadowwatch.models.library import LibraryVersion
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # ===== FREE TIER PUBLIC API =====
    
    async def track(
        self,
        user_id: int,
        entity_id: str,
        action: str,
        metadata: Optional[Dict] = None
    ):
        """
        Track user activity silently - FREE TIER
        
        No license required. No event limits.
        
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
        # FREE TIER: Use TrackingEngine
        return await self.tracking.track(user_id, entity_id, action, metadata)
    
    async def get_profile(self, user_id: int) -> Dict:
        """
        Get user's behavioral profile - FREE TIER
        
        No license required.
        
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
        
        Examples:
            profile = await sw.get_profile(user_id=123)
            print(f"User {user_id} has {profile['total_items']} interests")
        """
        # FREE TIER: Use ProfileEngine
        return await self.profile.get(user_id)
    
    async def get_library(self, user_id: int, limit: int = 15) -> Dict:
        """
        Get user's interest library - FREE TIER
        
        Alias for get_profile(). No license required.
        
        Args:
            user_id: User identifier
            limit: Maximum number of items (ignored for now, returns all)
        
        Returns:
            Same as get_profile()
        
        Examples:
            library = await sw.get_library(user_id=123)
        """
        # FREE TIER: Use LibraryEngine
        return await self.library.get(user_id, limit)
    
    async def verify_login(
        self,
        user_id: int,
        request_context: Dict
    ) -> Dict:
        """
        Calculate trust score for login/sensitive action
        
        NOTE: This is a legacy feature that requires license.
        Consider using Pro tier's calculate_continuity() for better ATO detection.
        
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
    
    # ===== PRO TIER PUBLIC API =====
    
    async def calculate_continuity(
        self,
        subject_id: str,
        context: Optional[Dict] = None
    ):
        """
        Calculate temporal actor persistence - PRO FEATURE
        
        Measures whether the current actor controlling an account
        remains coherent with the account's historical behavior.
        
        ⚠️ This is a Shadow Watch Pro feature.
        
        To use this feature:
        1. Install Pro: pip install shadowwatch-pro
        2. Get a license: https://shadowwatch.dev/pricing
        3. Initialize with license_key:
           
           sw = ShadowWatch(
               license_key="SW-PRO-XXXX-XXXX-XXXX-XXXX",
               database_url="postgresql://..."
           )
        
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
        
        Raises:
            LicenseError: If Pro features not enabled
        """
        if not self._pro_enabled:
            raise LicenseError(
                "calculate_continuity() requires Shadow Watch Pro.\n\n"
                "To use this feature:\n"
                "1. Install: pip install shadowwatch-pro\n"
                "2. Get license: https://shadowwatch.dev/pricing\n"
                "3. Add license_key parameter:\n"
                "   sw = ShadowWatch(\n"
                "       license_key='SW-PRO-XXXX-XXXX-XXXX-XXXX',\n"
                "       database_url='postgresql://...'\n"
                "   )"
            )
        
        return await self._pro.calculate_continuity(subject_id, context)
    
    async def detect_divergence(
        self,
        subject_id: str,
        window: Optional[int] = None
    ):
        """
        Detect behavioral divergence - PRO FEATURE
        
        Detects when behavioral evolution stops being self-consistent
        and starts being adversarial.
        
        ⚠️ This is a Shadow Watch Pro feature.
        
        Get started: https://shadowwatch.dev/pricing
        
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
        
        Raises:
            LicenseError: If Pro features not enabled
        """
        if not self._pro_enabled:
            raise LicenseError(
                "detect_divergence() requires Shadow Watch Pro.\n"
                "Get started: https://shadowwatch.dev/pricing"
            )
        
        return await self._pro.detect_divergence(subject_id, window)
    
    async def pre_auth_intent(
        self,
        identifier: str,
        observations: Dict
    ):
        """
        Analyze pre-authentication intent - PRO FEATURE
        
        Analyzes behavioral signals before authentication to detect
        credential stuffing and other pre-auth attacks.
        
        ⚠️ This is a Shadow Watch Pro feature.
        
        Get started: https://shadowwatch.dev/pricing
        
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
        
        Raises:
            LicenseError: If Pro features not enabled
        """
        if not self._pro_enabled:
            raise LicenseError(
                "pre_auth_intent() requires Shadow Watch Pro.\n"
                "Get started: https://shadowwatch.dev/pricing"
            )
        
        return await self._pro.pre_auth_intent(identifier, observations)
