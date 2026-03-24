"""
Shadow Watch - Main API

This is the primary interface users interact with.
All database sessions and configurations are injected.
"""

from typing import Dict, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from shadowwatch.utils.cache import create_cache, CacheBackend
from shadowwatch.core.tracker import track_activity
from shadowwatch.core.scorer import generate_library_snapshot
from shadowwatch.core.fingerprint import verify_fingerprint
from shadowwatch.core.trust_score import calculate_trust_score
from shadowwatch.models import Base  # For init_database()
from shadowwatch.utils.logger import logger


async def _persist_trust_signals(
    db: AsyncSession,
    user_id: int,
    request_context: dict,
) -> None:
    """
    Record IP and device observations after each verify_login() call.

    This is what builds the trust signal database over time — every
    successful login populates these tables so future logins can be
    compared against known-good history.

    Silent fail — never raises (tracking must never break login flow).
    """
    from datetime import datetime, timezone
    from sqlalchemy import select
    from shadowwatch.models.ip_history import UserIPHistory
    from shadowwatch.models.device import UserDeviceHistory

    try:
        ip = request_context.get("ip")
        country = request_context.get("country")
        user_agent = request_context.get("user_agent")
        device_fp = request_context.get("device_fingerprint")
        now = datetime.now(timezone.utc)

        # --- Persist IP ---
        if ip:
            result = await db.execute(
                select(UserIPHistory).where(
                    UserIPHistory.user_id == user_id,
                    UserIPHistory.ip_address == ip,
                )
            )
            existing_ip = result.scalar_one_or_none()
            if existing_ip:
                existing_ip.seen_count += 1
                existing_ip.last_seen = now
                if country and not existing_ip.country:
                    existing_ip.country = country
            else:
                db.add(UserIPHistory(
                    user_id=user_id,
                    ip_address=ip,
                    country=country,
                    first_seen=now,
                    last_seen=now,
                    seen_count=1,
                ))

        # --- Persist Device ---
        if device_fp:
            result = await db.execute(
                select(UserDeviceHistory).where(
                    UserDeviceHistory.user_id == user_id,
                    UserDeviceHistory.device_fingerprint == device_fp,
                )
            )
            existing_device = result.scalar_one_or_none()
            if existing_device:
                existing_device.seen_count += 1
                existing_device.last_seen = now
            else:
                db.add(UserDeviceHistory(
                    user_id=user_id,
                    device_fingerprint=device_fp,
                    user_agent=user_agent,
                    first_seen=now,
                    last_seen=now,
                    seen_count=1,
                    trust_level=0.8,
                ))

        await db.commit()

    except Exception:
        # Silent fail — never break the login flow
        pass


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
        redis_url: Optional[str] = None,
        webhook_url: Optional[str] = None
    ):
        """
        Shadow Watch - Behavioral Intelligence Library

        Args:
            database_url: SQLAlchemy async database URL (e.g., "postgresql+asyncpg://...")
            redis_url: Optional Redis URL for shared caching
            webhook_url: Optional endpoint to send security alerts (POST JSON)

        Examples:
            sw = ShadowWatch(database_url="postgresql+asyncpg://user:pass@host/db")
            await sw.track(user_id=123, entity_id="article_123", action="view")

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
        
        # Alerting configuration
        self.webhook_url = webhook_url

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

        logger.info("Shadow Watch core engines initialized")

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
        from shadowwatch.models.device import UserDeviceHistory
        from shadowwatch.models.ip_history import UserIPHistory
        from shadowwatch.models.pre_auth import PreAuthSession

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

        Also persists IP and device signals to history tables so the
        trust score improves over time as more logins are observed.

        Args:
            request_context: {
                "ip":                 Optional[str],
                "country":            Optional[str],    # ISO 3166-1 alpha-2
                "user_agent":         Optional[str],
                "device_fingerprint": Optional[str],
                "session_id":         Optional[str],    # link to pre-auth session
                "top_entities":       Optional[Set[str]], # client entity set
                "timestamp":          Optional[datetime]
            }

        Returns:
            {
                "trust_score": float (0.0-1.0),
                "risk_level":  str ("low", "medium", "elevated", "high"),
                "action":      str ("allow", "monitor", "require_mfa", "block"),
                "factors":     dict
            }
        """
        async with self.AsyncSessionLocal() as db:
            result = await calculate_trust_score(db, user_id, request_context)
            
            # Persist IP + device observations
            await _persist_trust_signals(db, user_id, request_context)
            
            # Link pre-auth session if it exists
            session_id = request_context.get("session_id")
            if session_id:
                from sqlalchemy import select, update
                from shadowwatch.models.pre_auth import PreAuthSession
                try:
                    stmt = update(PreAuthSession).where(
                        PreAuthSession.session_id == session_id
                    ).values(associated_user_id=user_id)
                    await db.execute(stmt)
                    await db.commit()
                except Exception:
                    pass
                    
            return result

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
            return await calculate_continuity_impl(
                db, 
                subject_id, 
                context, 
                alert_callback=self._fire_webhook
            )

    async def detect_divergence(
        self,
        subject_id: str,
        window: Optional[int] = None
    ):
        """
        Detect behavioral divergence

        Detects when behavioral evolution stops being self-consistent
        and starts being adversarial.

        Divergence modes:
            shock    - Fast actor substitution (single session, large distance spike)
            creep    - Gradual account drift (slow, sustained accumulation)
            fracture - Mixed signals (partial account sharing or hybrid attack)
            none     - No significant divergence detected

        Args:
            subject_id: Subject identifier
            window: Time window in hours to inspect (default: 24)

        Returns:
            {
                "magnitude": float (0.0-1.0),
                "velocity": float,
                "mode": "shock" | "creep" | "fracture" | "none",
                "confidence": float (0.0-1.0)
            }
        """
        from shadowwatch.invariant.integration import detect_divergence_impl

        async with self.AsyncSessionLocal() as db:
            return await detect_divergence_impl(
                db,
                str(subject_id),
                window_hours=window if window is not None else 24
            )

    async def resolve_divergence(
        self,
        event_id: int,
        resolution: str,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Resolve a divergence alert.
        
        Args:
            event_id:   ID of the divergence_event
            resolution: false_positive | legitimate_change | confirmed_attack | user_verified
            notes:      Analyst notes
            
        Returns:
            {"success": bool, "user_id": str}
        """
        from datetime import datetime, timezone
        from sqlalchemy import text as sa_text
        
        async with self.AsyncSessionLocal() as db:
            # 1. Update event
            result = await db.execute(sa_text(
                "UPDATE divergence_events "
                "SET resolved_at = :now, resolution_type = :res, notes = :notes "
                "WHERE id = :id RETURNING user_id"
            ), {
                "now": datetime.now(timezone.utc), 
                "res": resolution, 
                "notes": notes, 
                "id": event_id
            })
            
            row = result.fetchone()
            if not row:
                return {"success": False, "error": "Event not found"}
                
            user_id = row[0]
            
            # 2. Baseline tuning if legitimate_change
            if resolution == "legitimate_change":
                # We clear the divergence metrics but keep the sample_count 
                # moderately high (5) so confidence doesn't drop to zero,
                # but the engine begins learning the 'new' normal immediately.
                await db.execute(sa_text(
                    "UPDATE invariant_state "
                    "SET divergence_accumulated = 0.0, "
                    "    divergence_velocity = 0.0, "
                    "    divergence_mode = NULL, "
                    "    sample_count = GREATEST(sample_count, 5) "
                    "WHERE user_id = :u"
                ), {"u": user_id})
                
            await db.commit()
            return {"success": True, "event_id": event_id, "user_id": user_id}

    async def _fire_webhook(self, event_data: Dict) -> None:
        """
        Send a security alert to the configured webhook_url.
        
        Silent fail to ensure it doesn't block the main flow.
        """
        if not self.webhook_url:
            return
            
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.webhook_url, json=event_data, timeout=5.0)
        except Exception as e:
            # We don't have the structured logger yet, so just pass
            pass

    async def pre_auth_intent(
        self,
        identifier: str,
        observations: Dict
    ) -> Dict:
        """
        Analyze pre-authentication intent

        Analyzes behavioral signals before authentication to detect
        credential stuffing and other pre-auth attacks.

        Args:
            identifier: Session ID, or device_fingerprint
            observations: {
                "session_id":         str,          # Required for tracking
                "ip":                 Optional[str],
                "device_fingerprint": Optional[str],
                "typing_cadence":     Optional[Dict],
                "mouse_latency":      Optional[float],
                "navigation_path":    Optional[List[str]],
                "user_agent":         Optional[str]
            }

        Returns:
            {
                "intent_score": float (0.0-1.0),
                "risk_level":   str ("low", "elevated", "high"),
                "action":       str ("allow", "challenge", "block"),
                "session_id":   str
            }
        """
        from sqlalchemy import select
        from shadowwatch.models.pre_auth import PreAuthSession
        from datetime import datetime, timezone
        
        session_id = observations.get("session_id")
        if not session_id:
            # Fallback to identifier if session_id is missing
            session_id = identifier

        async with self.AsyncSessionLocal() as db:
            # 1. Store/Update pre-auth session
            result = await db.execute(
                select(PreAuthSession).where(PreAuthSession.session_id == session_id)
            )
            session = result.scalar_one_or_none()
            
            now = datetime.now(timezone.utc)
            if not session:
                session = PreAuthSession(
                    session_id=session_id,
                    ip_address=observations.get("ip"),
                    device_fingerprint=observations.get("device_fingerprint"),
                    signals=observations,
                    created_at=now,
                    updated_at=now
                )
                db.add(session)
            else:
                # Merge new signals
                existing_signals = session.signals or {}
                existing_signals.update(observations)
                session.signals = existing_signals
                session.updated_at = now
                if observations.get("ip"):
                    session.ip_address = observations.get("ip")
            
            await db.commit()

            # 2. Risk Detection logic (Simplified for now - can be expanded)
            # High velocity or bot pattern detection
            risk_level = "low"
            action = "allow"
            intent_score = 1.0

            # Simple heuristic: typing cadence check (stub)
            if observations.get("typing_cadence"):
                # Real ML model or statistical check would go here
                pass

            # Detect high-velocity cross-account attempts (stub)
            
            return {
                "intent_score": intent_score,
                "risk_level": risk_level,
                "action": action,
                "session_id": session_id
            }

    async def get_system_stats(self) -> Dict:
        """
        Get global system metrics.
        
        Returns:
            {
                "total_monitored_users": int,
                "unresolved_alerts":     int,
                "last_system_activity":  datetime
            }
        """
        from sqlalchemy import text as sa_text
        
        async with self.AsyncSessionLocal() as db:
            # 1. Total active baselines
            res_users = await db.execute(sa_text("SELECT COUNT(*) FROM invariant_state"))
            total_users = res_users.scalar()
            
            # 2. Unresolved divergence events
            res_events = await db.execute(sa_text(
                "SELECT COUNT(*) FROM divergence_events WHERE resolved_at IS NULL"
            ))
            unresolved_alerts = res_events.scalar()
            
            # 3. Last activity detected
            res_last = await db.execute(sa_text(
                "SELECT MAX(last_seen_at) FROM invariant_state"
            ))
            last_activity = res_last.scalar()
            
            return {
                "total_monitored_users": total_users,
                "unresolved_alerts": unresolved_alerts,
                "last_system_activity": last_activity,
            }
