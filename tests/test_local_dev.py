"""
Test Shadow Watch - Local Development Setup

Demonstrates using Shadow Watch without Redis (in-memory cache).
Perfect for:
- Local testing
- Development
- CI/CD pipelines
- Demo applications

No license key required.
"""

import asyncio
import os
from shadowwatch import ShadowWatch
from shadowwatch.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test"
)


async def test_local_dev_mode():
    """Test Shadow Watch in local dev mode (no Redis)"""

    print("=" * 70)
    print("Shadow Watch - Local Development Mode Test")
    print("=" * 70)
    print()

    print("🔧 Step 1: Initializing Shadow Watch (no Redis)...")
    sw = ShadowWatch(
        database_url=DATABASE_URL,
        redis_url=None  # In-memory cache for local dev
    )
    await sw.init_database()
    print("✅ Shadow Watch initialized")
    print()

    user_id = 1

    print("📊 Step 2: Testing activity tracking...")
    activities = [
        ("AAPL", "view"),
        ("MSFT", "view"),
        ("GOOGL", "search"),
        ("AAPL", "trade"),
        ("TSLA", "watchlist"),
    ]

    for entity_id, action in activities:
        await sw.track(
            user_id=user_id,
            entity_id=entity_id,
            action=action,
            metadata={"test": "local_dev"}
        )
        print(f"   ✓ Tracked: {action.ljust(10)} {entity_id}")

    print()
    print(f"✅ Tracked {len(activities)} events")
    print()

    print("👤 Step 3: Getting user profile...")
    profile = await sw.get_profile(user_id=user_id)
    print(f"✅ Profile retrieved:")
    print(f"   Total items: {profile['total_items']}")
    print(f"   Fingerprint: {profile['fingerprint'][:32]}...")
    print()

    print("🔐 Step 4: Testing login verification...")
    trust = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": "127.0.0.1",
            "user_agent": "Mozilla/5.0",
            "library_fingerprint": profile['fingerprint']
        }
    )
    print(f"✅ Trust score: {trust['trust_score']:.2f}  Action: {trust['action']}")
    print()

    print("=" * 70)
    print("✅ Local Dev Mode Test Complete!")
    print("=" * 70)
    print()
    print("Features tested:")
    print("  ✅ No license required")
    print("  ✅ No Redis required (in-memory cache)")
    print("  ✅ Activity tracking works")
    print("  ✅ Profile generation works")
    print("  ✅ Trust scoring works")
    print()


if __name__ == "__main__":
    print()
    print("Shadow Watch - Local Development Mode Tests")
    print()
    asyncio.run(test_local_dev_mode())
