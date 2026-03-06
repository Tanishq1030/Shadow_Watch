"""
Simple smoke test - Shadow Watch open source (no pytest dependency)
"""
import asyncio
from shadowwatch import ShadowWatch

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test"


async def simple_test():
    print("\n" + "="*70)
    print("Shadow Watch - Open Source Smoke Test")
    print("="*70)
    print()

    print("TEST 1: Initialize Shadow Watch...")
    sw = ShadowWatch(database_url=DATABASE_URL)
    await sw.init_database()
    print("✅ SUCCESS: Shadow Watch initialized")
    print()

    print("TEST 2: Track events...")
    for i in range(5):
        await sw.track(user_id=1, entity_id=f"STOCK_{i}", action="view")
        print(f"   Event {i+1}/5 tracked")
    print("✅ SUCCESS: Events tracked")
    print()

    print("TEST 3: Get profile...")
    profile = await sw.get_profile(user_id=1)
    assert profile is not None
    print(f"✅ SUCCESS: Profile has {profile['total_items']} items")
    print()

    print("="*70)
    print("🎉 ALL TESTS PASSED! Shadow Watch is fully open source.")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(simple_test())
