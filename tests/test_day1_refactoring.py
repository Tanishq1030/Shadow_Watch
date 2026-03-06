"""
Test Shadow Watch Core Features

Verifies all features work without any license key.
"""
import pytest
from shadowwatch import ShadowWatch

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test"


@pytest.mark.asyncio
async def test_all_features_available():
    """All Shadow Watch features should work without a license key"""

    sw = ShadowWatch(database_url=DATABASE_URL)
    await sw.init_database()

    # Core tracking
    await sw.track(user_id=123, entity_id="AAPL", action="view")
    profile = await sw.get_profile(user_id=123)
    library = await sw.get_library(user_id=123)

    assert profile is not None
    assert library is not None
    print("✅ Tracking and profiles work!")


@pytest.mark.asyncio
async def test_continuity_available():
    """calculate_continuity() should be freely available"""

    sw = ShadowWatch(database_url=DATABASE_URL)
    await sw.init_database()

    # Track some activity first
    await sw.track(user_id=456, entity_id="MSFT", action="view")

    # Continuity should work without any license
    result = await sw.calculate_continuity("456")
    assert result is not None
    assert "score" in result
    print("✅ calculate_continuity() works freely!")


@pytest.mark.asyncio
async def test_all_methods_visible():
    """All methods should be visible in dir()"""

    sw = ShadowWatch(database_url=DATABASE_URL)

    methods = dir(sw)
    assert "track" in methods
    assert "get_profile" in methods
    assert "get_library" in methods
    assert "calculate_continuity" in methods
    assert "detect_divergence" in methods
    assert "pre_auth_intent" in methods
    print("✅ All methods visible in dir()!")


if __name__ == "__main__":
    import asyncio

    print("\n" + "="*60)
    print("Testing Shadow Watch - All Features Free")
    print("="*60 + "\n")

    asyncio.run(test_all_features_available())
    asyncio.run(test_continuity_available())
    asyncio.run(test_all_methods_visible())

    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60 + "\n")
