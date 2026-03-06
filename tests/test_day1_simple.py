"""
Quick smoke test - all Shadow Watch features (no pytest dependency)
"""
import asyncio
from shadowwatch import ShadowWatch

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test"


async def test_core_features():
    print("\n1️⃣ Testing core features (no license needed)...")

    sw = ShadowWatch(database_url=DATABASE_URL)
    await sw.init_database()

    await sw.track(user_id=123, entity_id="AAPL", action="view")
    print("   ✅ track() works")

    profile = await sw.get_profile(user_id=123)
    print("   ✅ get_profile() works")

    library = await sw.get_library(user_id=123)
    print("   ✅ get_library() works")


async def test_advanced_features():
    print("\n2️⃣ Testing advanced features (all free)...")

    sw = ShadowWatch(database_url=DATABASE_URL)
    await sw.init_database()

    await sw.track(user_id=999, entity_id="TSLA", action="view")

    result = await sw.calculate_continuity("999")
    print(f"   ✅ calculate_continuity() works — score: {result.get('score', 'N/A')}")


def test_all_methods_visible():
    print("\n3️⃣ Testing methods visible in dir()...")

    sw = ShadowWatch(database_url=DATABASE_URL)
    methods = dir(sw)

    assert "track" in methods
    assert "get_profile" in methods
    assert "get_library" in methods
    assert "calculate_continuity" in methods
    assert "detect_divergence" in methods
    assert "pre_auth_intent" in methods
    print("   ✅ All methods visible")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Shadow Watch - Open Source Smoke Test")
    print("="*70)

    asyncio.run(test_core_features())
    asyncio.run(test_advanced_features())
    test_all_methods_visible()

    print("\n" + "="*70)
    print("✅ All tests passed! Shadow Watch is fully free.")
    print("="*70 + "\n")
