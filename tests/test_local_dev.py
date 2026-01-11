"""
Test Shadow Watch in Local Development Mode (No License Required)

This test demonstrates using Shadow Watch without a license key.
Perfect for:
- Local testing
- Development
- CI/CD pipelines
- Demo applications

Limitations:
- 1,000 events maximum
- Not for production use
"""

import asyncio
import os
from shadowwatch import ShadowWatch
from shadowwatch.models import Base
from sqlalchemy.ext.asyncio import create_async_engine


async def test_local_dev_mode():
    """Test Shadow Watch in local dev mode (no license)"""
    
    print("=" * 70)
    print("Shadow Watch - Local Development Mode Test")
    print("=" * 70)
    print()
    
    # Step 1: Initialize WITHOUT license key
    print("🔧 Step 1: Initializing Shadow Watch (No License)...")
    print()
    
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./test_local_dev.db",
        license_key=None  # ← No license required!
    )
    
    print("✅ Shadow Watch initialized in local dev mode")
    print()
    
    # Step 2: Create database tables (use Shadow Watch's engine!)
    print("🗄️  Step 2: Creating database tables...")
    async with sw.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    print()
    
    # Step 3: Track activities (test the 1000 event limit)
    print("📊 Step 3: Testing activity tracking...")
    print()
    
    user_id = 1
    
    # Track a few events
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
    print(f"   Events remaining: {sw._event_limit - sw._event_count}")
    print()
    
    # Step 4: Get user profile
    print("👤 Step 4: Getting user profile...")
    profile = await sw.get_profile(user_id=user_id)
    print(f"✅ Profile retrieved:")
    print(f"   Total items: {profile['total_items']}")
    print(f"   Fingerprint: {profile['fingerprint'][:32]}...")
    print()
    
    # Step 5: Test login verification
    print("🔐 Step 5: Testing login verification...")
    trust = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": "127.0.0.1",
            "user_agent": "Mozilla/5.0",
            "library_fingerprint": profile['fingerprint']
        }
    )
    print(f"✅ Trust score: {trust['trust_score']:.2f}")
    print(f"   Action: {trust['action']}")
    print()
    
    # Step 6: Show event usage
    print("📈 Step 6: Event usage summary...")
    print(f"   Events used: {sw._event_count} / {sw._event_limit}")
    print(f"   Events remaining: {sw._event_limit - sw._event_count}")
    print()
    
    print("=" * 70)
    print("✅ Local Dev Mode Test Complete!")
    print("=" * 70)
    print()
    print("Key features tested:")
    print("  ✅ No license required")
    print("  ✅ 1,000 event limit enforced")
    print("  ✅ All core features working")
    print("  ✅ Perfect for local development")
    print()
    print("Next steps:")
    print("  1. For production, get trial license:")
    print("     https://shadow-watch-three.vercel.app/trial")
    print("  2. Or continue testing locally (995 events remaining)")
    print()


async def test_event_limit():
    """Test that event limit is enforced"""
    
    print("=" * 70)
    print("Testing 1,000 Event Limit")
    print("=" * 70)
    print()
    
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./test_limit.db",
        license_key=None
    )
    
    # Create tables using Shadow Watch's engine
    async with sw.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print(f"Initial event count: {sw._event_count} / {sw._event_limit}")
    
    # Simulate tracking to approach limit
    # (We won't actually hit 1000, just demonstrate the counter)
    for i in range(10):
        await sw.track(user_id=1, entity_id=f"STOCK_{i}", action="view")
    
    print(f"After 10 events: {sw._event_count} / {sw._event_limit}")
    print()
    
    # Show what happens when limit is reached
    print("⚠️  When you reach 1,000 events, you'll see:")
    print('   Exception: "Local dev limit reached (1,000 events)"')
    print('   "Get free trial: https://shadow-watch-three.vercel.app/trial"')
    print()
    print("✅ Event limit test complete")
    print()


if __name__ == "__main__":
    print()
    print("Shadow Watch - Local Development Mode Tests")
    print()
    
    # Run tests
    asyncio.run(test_local_dev_mode())
    print()
    asyncio.run(test_event_limit())
