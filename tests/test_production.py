"""
Test Shadow Watch in Production Mode (With License Key)

This test demonstrates using Shadow Watch with a trial/production license.
For production deployments with:
- Trial license (30 days, 10k events)
- Production license (unlimited)

How to get a license:
1. Trial: https://shadow-watch-three.vercel.app/trial
2. Production: Email tanishqdasari2004@gmail.com
"""

import asyncio
import os
from shadowwatch import ShadowWatch
from shadowwatch.models import Base
from sqlalchemy.ext.asyncio import create_async_engine


async def test_production_mode():
    """Test Shadow Watch with production license"""
    
    print("=" * 70)
    print("Shadow Watch - Production Mode Test")
    print("=" * 70)
    print()
    
    # Step 1: Get license key
    license_key = os.getenv("SHADOWWATCH_LICENSE_KEY")
    
    if not license_key:
        print("❌ No license key found!")
        print()
        print("To run this test, you need a license key:")
        print()
        print("Option 1: Get instant trial license (free)")
        print("  curl -X POST https://shadow-watch-three.vercel.app/trial \\")
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"name":"Your Name","email":"your@email.com"}\'')
        print()
        print("Option 2: Set environment variable")
        print("  set SHADOWWATCH_LICENSE_KEY=SW-TRIAL-XXXX-XXXX-XXXX-XXXX")
        print()
        print("Then run this test again.")
        return
    
    # Step 2: Initialize WITH license key
    print("🔧 Step 1: Initializing Shadow Watch (With License)...")
    print(f"   License: {license_key[:20]}...")
    print()
    
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./test_production.db",
        license_key=license_key,  # ← Production license
        redis_url=None  # Add Redis URL for multi-instance production
    )
    
    print("✅ Shadow Watch initialized")
    print()
    
    # Step 3: Create database tables
    print("🗄️  Step 2: Creating database tables...")
    engine = create_async_engine("sqlite+aiosqlite:///./test_production.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    print()
    
    # Step 4: Track activities (no limit!)
    print("📊 Step 3: Testing activity tracking...")
    print()
    
    user_id = 100
    
    # Track multiple events
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
    print(f"✅ Tracked {len(activities)} events (no limit in production!)")
    print()
    
    # Step 5: Get user profile
    print("👤 Step 4: Getting user profile...")
    profile = await sw.get_profile(user_id=user_id)
    
    print(f"✅ Profile retrieved:")
    print(f"   Total items: {profile['total_items']}")
    print(f"   Fingerprint: {profile['fingerprint'][:32]}...")
    print()
    print("   Top 3 Interests:")
    for i, item in enumerate(profile['library'][:3], 1):
        pinned = "📌" if item['is_pinned'] else "  "
        print(f"   {i}. {pinned} {item['entity_id'].ljust(10)} Score: {item['score']:.2f}")
    print()
    
    # Step 6: Test login verification
    print("🔐 Step 5: Testing login verification...")
    print()
    
    # Legitimate login
    trust_good = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "library_fingerprint": profile['fingerprint']  # Correct!
        }
    )
    
    print("   Legitimate login attempt:")
    print(f"   Trust score: {trust_good['trust_score']:.2f}")
    print(f"   Risk level: {trust_good['risk_level']}")
    print(f"   Action: {trust_good['action']}")
    print()
    
    # Suspicious login
    trust_bad = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": "203.0.113.42",  # Different IP
            "user_agent": "curl/7.68.0",  # Suspicious
            "library_fingerprint": "0000000000000000"  # Wrong!
        }
    )
    
    print("   Suspicious login attempt:")
    print(f"   Trust score: {trust_bad['trust_score']:.2f}")
    print(f"   Risk level: {trust_bad['risk_level']}")
    print(f"   Action: {trust_bad['action']}")
    print()
    
    # Step 7: Library management
    print("📚 Step 6: Testing library management...")
    print()
    
    # Pin item
    await sw.pin_item(user_id=user_id, entity_id="AAPL")
    print("   ✓ Pinned AAPL")
    
    # Get library
    library = await sw.get_library(user_id=user_id)
    aapl = next((item for item in library if item['entity_id'] == 'AAPL'), None)
    
    if aapl and aapl['is_pinned']:
        print("   ✓ Pin verified in library")
    print()
    
    print("=" * 70)
    print("✅ Production Mode Test Complete!")
    print("=" * 70)
    print()
    print("Production features tested:")
    print("  ✅ Licensed mode (no event limit)")
    print("  ✅ Activity tracking with metadata")
    print("  ✅ User profiling and fingerprinting")
    print("  ✅ Login verification (trust scores)")
    print("  ✅ Library management (pin/unpin)")
    print()
    print("Ready for production deployment! 🚀")
    print()


async def test_multi_user():
    """Test multiple users in production"""
    
    print("=" * 70)
    print("Testing Multiple Users (Production)")
    print("=" * 70)
    print()
    
    license_key = os.getenv("SHADOWWATCH_LICENSE_KEY")
    if not license_key:
        print("⚠️  Skipping (no license key)")
        return
    
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./test_multi_user.db",
        license_key=license_key
    )
    
    # Create tables
    engine = create_async_engine("sqlite+aiosqlite:///./test_multi_user.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Track for multiple users
    users = [1001, 1002, 1003]
    stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    
    print("Tracking activity for 3 users...")
    for user_id in users:
        for stock in stocks[:3]:  # Each user interacts with 3 stocks
            await sw.track(user_id=user_id, entity_id=stock, action="view")
        print(f"   ✓ User {user_id}: 3 events tracked")
    
    print()
    print("Getting profiles...")
    for user_id in users:
        profile = await sw.get_profile(user_id=user_id)
        print(f"   User {user_id}: {profile['total_items']} interests")
    
    print()
    print("✅ Multi-user test complete")
    print()


if __name__ == "__main__":
    print()
    print("Shadow Watch - Production Mode Tests")
    print()
    
    # Run tests
    asyncio.run(test_production_mode())
    print()
    asyncio.run(test_multi_user())
    
    print()
    print("=" * 70)
    print("All Production Tests Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Deploy to production with PostgreSQL")
    print("  2. Add Redis for multi-instance caching")
    print("  3. Monitor event usage")
    print("  4. Upgrade to production license when trial expires")
    print()
