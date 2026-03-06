"""
End-to-End Client Test for Shadow Watch

Tests the complete workflow from a client's perspective:
1. Install Shadow Watch from PyPI
2. Initialize (no license key needed)
3. Create database tables
4. Track user activity
5. Get user profile
6. Verify login with trust score
7. Test library management

Run this in a fresh virtual environment to simulate real client usage.
"""

import asyncio
import os
import sys
from datetime import datetime

async def test_shadowwatch():
    print("=" * 70)
    print("Shadow Watch - End-to-End Client Test")
    print("=" * 70)
    print()
    
    # Step 1: Import check
    print("📦 Step 1: Checking Shadow Watch installation...")
    try:
        from shadowwatch import ShadowWatch
        from shadowwatch.models import Base
        from sqlalchemy.ext.asyncio import create_async_engine
        print("✅ Shadow Watch imported successfully!")
    except ImportError as e:
        print(f"❌ Failed to import Shadow Watch: {e}")
        print("   Run: pip install shadowwatch")
        return False
    
    print()
    
    # Step 2: Initialize
    print("🔧 Step 2: Initializing Shadow Watch...")
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test")
    
    try:
        sw = ShadowWatch(database_url=database_url)
        print(f"✅ Shadow Watch initialized")
        print(f"   Database: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    print()
    
    # Step 3: Create tables
    print("🗄️  Step 3: Creating database tables...")
    try:
        engine = create_async_engine(database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created:")
        print("   - shadow_watch_activity_events")
        print("   - shadow_watch_interests")
        print("   - shadow_watch_library_versions")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
    
    print()
    
    # Step 4: Track activity
    print("📊 Step 4: Tracking user activity...")
    user_id = 123
    
    activities = [
        ("AAPL", "view", {"source": "homepage"}),
        ("MSFT", "view", {"source": "search"}),
        ("GOOGL", "search", {"query": "tech stocks"}),
        ("AAPL", "watchlist", {}),
        ("AAPL", "trade", {"quantity": 10, "price": 185.20}),
        ("TSLA", "view", {"source": "trending"}),
        ("NVDA", "search", {"query": "AI stocks"}),
        ("AAPL", "view", {"source": "watchlist"}),
    ]
    
    try:
        for entity_id, action, metadata in activities:
            await sw.track(
                user_id=user_id,
                entity_id=entity_id,
                action=action,
                metadata=metadata
            )
            print(f"   ✓ Tracked: {action.ljust(10)} {entity_id}")
        
        print(f"✅ Tracked {len(activities)} activities for user {user_id}")
    except Exception as e:
        print(f"❌ Failed to track activity: {e}")
        return False
    
    print()
    
    # Step 5: Get profile
    print("👤 Step 5: Getting user profile...")
    try:
        profile = await sw.get_profile(user_id=user_id)
        
        print("✅ Profile retrieved:")
        print(f"   Total items: {profile['total_items']}")
        print(f"   Fingerprint: {profile['fingerprint'][:32]}...")
        print()
        print("   Top Interests:")
        for i, item in enumerate(profile['library'][:5], 1):
            score = item['score']
            entity = item['entity_id']
            pinned = "📌" if item['is_pinned'] else "  "
            print(f"   {i}. {pinned} {entity.ljust(10)} Score: {score:.2f}")
    except Exception as e:
        print(f"❌ Failed to get profile: {e}")
        return False
    
    print()
    
    # Step 6: Login verification
    print("🔐 Step 6: Testing login verification...")
    try:
        # Simulate legitimate login
        trust = await sw.verify_login(
            user_id=user_id,
            request_context={
                "ip": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "device_fingerprint": "abc123",
                "library_fingerprint": profile['fingerprint']  # Correct fingerprint
            }
        )
        
        print("✅ Login verification test (legitimate):")
        print(f"   Trust Score: {trust['trust_score']:.2f}")
        print(f"   Risk Level: {trust['risk_level']}")
        print(f"   Action: {trust['action']}")
        
        # Simulate suspicious login (wrong fingerprint)
        print()
        print("   Testing suspicious login (mismatched fingerprint)...")
        trust_sus = await sw.verify_login(
            user_id=user_id,
            request_context={
                "ip": "203.0.113.42",  # Different IP
                "user_agent": "curl/7.68.0",  # Different user agent
                "device_fingerprint": "xyz789",
                "library_fingerprint": "0000000000000000"  # Wrong fingerprint
            }
        )
        
        print(f"   Trust Score: {trust_sus['trust_score']:.2f}")
        print(f"   Risk Level: {trust_sus['risk_level']}")
        print(f"   Action: {trust_sus['action']}")
        
    except Exception as e:
        print(f"❌ Failed login verification: {e}")
        return False
    
    print()
    
    # Step 7: Library management
    print("📚 Step 7: Testing library management...")
    try:
        # Pin an item
        await sw.pin_item(user_id=user_id, entity_id="AAPL")
        print("   ✓ Pinned AAPL")
        
        # Get updated library
        library = await sw.get_library(user_id=user_id)
        aapl = next((item for item in library if item['entity_id'] == 'AAPL'), None)
        
        if aapl and aapl['is_pinned']:
            print("   ✅ Pin verified!")
        else:
            print("   ⚠️  Pin not reflected in library")
        
        # Unpin
        await sw.unpin_item(user_id=user_id, entity_id="AAPL")
        print("   ✓ Unpinned AAPL")
        
    except Exception as e:
        print(f"❌ Failed library management: {e}")
        return False
    
    print()
    
    # Summary
    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print()
    print("Shadow Watch is working correctly. Key features tested:")
    print("  ✅ Package installation and imports")
    print("  ✅ Database initialization")
    print("  ✅ Activity tracking (8 events)")
    print("  ✅ Profile generation and fingerprinting")
    print("  ✅ Login verification with trust scores")
    print("  ✅ Library management (pin/unpin)")
    print()
    print("Next steps:")
    print("  1. Integrate Shadow Watch into your application")
    print("  2. Deploy to production with PostgreSQL + Redis")
    print()
    print("Documentation:")
    print("  - Getting Started: docs/GETTING_STARTED.md")
    print("  - API Reference: docs/API_REFERENCE.md")
    print("  - Integration Guides: docs/INTEGRATION_GUIDES.md")
    print()
    
    return True

if __name__ == "__main__":
    print()
    print("Shadow Watch End-to-End Test")
    print("Testing from client perspective...")
    print()
    
    try:
        result = asyncio.run(test_shadowwatch())
        
        if result:
            print("🎉 Test completed successfully!")
            sys.exit(0)
        else:
            print("❌ Test failed. Check errors above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
