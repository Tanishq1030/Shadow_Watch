"""
Shadow Watch Standalone Usage Example

Shows how to use Shadow Watch directly without framework integration
"""

import asyncio
from shadowwatch import ShadowWatch


async def main():
    """
    Standalone Shadow Watch demo
    
    This example shows direct API usage without FastAPI/Django middleware.
    Good for understanding core functionality.
    """
    
    # 1. Initialize Shadow Watch
    print("🌑 Initializing Shadow Watch...")
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./shadow_watch_demo.db",
        license_key="SW-TRIAL-0001-2026-A1B2"  # Replace with your trial key
    )
    print("✅ Shadow Watch initialized\n")
    
    # 2. Track some user activity
    print("📊 Tracking user activity...")
    
    user_id = 123
    
    # User views AAPL
    await sw.track(user_id=user_id, entity_id="AAPL", action="view")
    print(f"  ✓ Tracked: User {user_id} viewed AAPL")
    
    # User searches for MSFT
    await sw.track(user_id=user_id, entity_id="MSFT", action="search")
    print(f"  ✓ Tracked: User {user_id} searched MSFT")
    
    # User trades TSLA (high weight!)
    await sw.track(
        user_id=user_id,
        entity_id="TSLA",
        action="trade",
        metadata={"portfolio_value": 5000.0, "shares": 10}
    )
    print(f"  ✓ Tracked: User {user_id} traded TSLA\n")
    
    # 3. Get user's behavioral profile
    print("🧠 Generating behavioral profile...")
    profile = await sw.get_profile(user_id=user_id)
    
    print(f"\n📚 Shadow Watch Profile for User {user_id}:")
    print(f"  Total Items: {profile['total_items']}")
    print(f"  Pinned Count: {profile['pinned_count']}")
    print(f"  Fingerprint: {profile['fingerprint'][:16]}...")
    
    print("\n  Top Interests:")
    for item in profile['library'][:3]:
        print(f"    • {item['symbol']}: score={item['score']} (tier {item['tier']})")
    
    # 4. Verify login (trust score)
    print("\n🔐 Calculating trust score for login verification...")
    
    trust_result = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "library_fingerprint": profile['fingerprint']  # From client cache
        }
    )
    
    print(f"\n  Trust Score: {trust_result['trust_score']}")
    print(f"  Risk Level: {trust_result['risk_level']}")
    print(f"  Action: {trust_result['action']}")
    print(f"\n  Factor Breakdown:")
    for factor, score in trust_result['factors'].items():
        print(f"    • {factor}: {score}")
    
    print("\n✅ Demo complete!")
    print("\n💡 Key Takeaways:")
    print("  1. Shadow Watch tracks silently (no user interaction)")
    print("  2. Trades are weighted 10x higher than views")
    print("  3. Fingerprints are generated automatically")
    print("  4. Trust scores protect against account takeover")


if __name__ == "__main__":
    asyncio.run(main())
