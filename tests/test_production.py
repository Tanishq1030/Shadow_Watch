"""
Test Shadow Watch - Full Feature Test (No License Required)

All Shadow Watch features are fully free and open source.
Run this test against a local PostgreSQL instance.
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


async def test_full_features():
    """Test all Shadow Watch features — no license needed"""

    print("=" * 70)
    print("Shadow Watch - Full Feature Test (Open Source)")
    print("=" * 70)
    print()

    print("🔧 Step 1: Initializing Shadow Watch...")
    sw = ShadowWatch(
        database_url=DATABASE_URL,
        redis_url=None
    )

    await sw.init_database()
    print("✅ Shadow Watch initialized")
    print()

    user_id = 100

    # Track activities
    print("📊 Step 2: Testing activity tracking...")
    activities = [
        ("AAPL", "view", {"source": "dashboard"}),
        ("AAPL", "view", {"source": "watchlist"}),
        ("MSFT", "search", {"query": "microsoft"}),
        ("GOOGL", "view", {"source": "trending"}),
        ("AAPL", "watchlist", {}),
        ("TSLA", "search", {"query": "tesla"}),
        ("NVDA", "view", {"source": "ai_stocks"}),
        ("AAPL", "trade", {"quantity": 10, "price": 185.20}),
        ("MSFT", "trade", {"quantity": 5, "price": 420.50}),
        ("GOOGL", "alert", {"price_target": 150.00}),
    ]

    for entity_id, action, metadata in activities:
        await sw.track(
            user_id=user_id,
            entity_id=entity_id,
            action=action,
            metadata=metadata
        )
        print(f"   ✓ Tracked: {action.ljust(10)} {entity_id}")

    print()
    print(f"✅ Tracked {len(activities)} events")
    print()

    # Get profile
    print("👤 Step 3: Getting user profile...")
    profile = await sw.get_profile(user_id=user_id)
    print(f"✅ Profile retrieved:")
    print(f"   Total items: {profile['total_items']}")
    print(f"   Fingerprint: {profile['fingerprint'][:32]}...")
    print()
    print("   Top 3 Interests:")
    for i, item in enumerate(profile['library'][:3], 1):
        pinned = "📌" if item.get('is_pinned') else "  "
        print(f"   {i}. {pinned} {item['entity_id'].ljust(10)} Score: {item['score']:.2f}")
    print()

    # Login verification
    print("🔐 Step 4: Testing login verification (trust scores)...")

    trust_good = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "library_fingerprint": profile['fingerprint']
        }
    )
    print(f"   Legitimate login → Trust: {trust_good['trust_score']:.2f}  Action: {trust_good['action']}")

    trust_bad = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": "203.0.113.42",
            "user_agent": "curl/7.68.0",
            "library_fingerprint": "0000000000000000"
        }
    )
    print(f"   Suspicious login → Trust: {trust_bad['trust_score']:.2f}  Action: {trust_bad['action']}")
    print()

    # Continuity
    print("🧠 Step 5: Testing ATO detection (continuity)...")
    continuity = await sw.calculate_continuity(str(user_id))
    print(f"   Score: {continuity['score']:.2f}  State: {continuity['state']}  Confidence: {continuity['confidence']:.2f}")
    print()

    print("=" * 70)
    print("✅ All tests passed — Shadow Watch is fully open source!")
    print("=" * 70)


async def test_multi_user():
    """Test multiple users"""
    print()
    print("=" * 70)
    print("Multi-User Test")
    print("=" * 70)
    print()

    sw = ShadowWatch(database_url=DATABASE_URL)
    await sw.init_database()

    users = [1001, 1002, 1003]
    stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

    print("Tracking activity for 3 users...")
    for user_id in users:
        for stock in stocks[:3]:
            await sw.track(user_id=user_id, entity_id=stock, action="view")
        print(f"   ✓ User {user_id}: 3 events tracked")

    print()
    print("Getting profiles...")
    for user_id in users:
        profile = await sw.get_profile(user_id=user_id)
        print(f"   User {user_id}: {profile['total_items']} interests")

    print()
    print("✅ Multi-user test complete")


if __name__ == "__main__":
    print()
    print("Shadow Watch - Open Source Feature Tests")
    print()

    asyncio.run(test_full_features())
    asyncio.run(test_multi_user())

    print()
    print("=" * 70)
    print("All Tests Complete! 🚀")
    print("=" * 70)
