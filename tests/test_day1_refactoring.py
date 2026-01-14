"""
Test Shadow Watch Free Tier (Day 1 Refactoring)

Verifies that free tier works without license.
"""
import pytest
from shadowwatch import ShadowWatch, LicenseError


@pytest.mark.asyncio
async def test_free_tier_no_license_required():
    """Free tier should work without license"""
    
    # Should not raise any errors
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///test_free_tier.db"
        # NO license_key parameter
    )
    
    # Initialize database
    await sw.init_database()
    
    # Free tier methods should work
    await sw.track(user_id=123, entity_id="AAPL", action="view")
    profile = await sw.get_profile(user_id=123)
    library = await sw.get_library(user_id=123)
    
    assert profile is not None
    assert library is not None
    print("✅ Free tier works without license!")


@pytest.mark.asyncio
async def test_pro_methods_raise_license_error():
    """Pro methods should raise LicenseError without license"""
    
    sw = ShadowWatch(database_url="sqlite+aiosqlite:///test_free_tier.db")
    
    # Pro methods should raise LicenseError
    with pytest.raises(LicenseError) as exc_info:
        await sw.calculate_continuity("user_123")
    
    error_msg = str(exc_info.value)
    assert "Shadow Watch Pro" in error_msg
    assert "pip install shadowwatch-pro" in error_msg
    print("✅ Pro methods correctly raise LicenseError!")


@pytest.mark.asyncio
async def test_pro_methods_visible_in_dir():
    """Pro methods should be visible for autocomplete"""
    
    sw = ShadowWatch(database_url="sqlite+aiosqlite:///test_free_tier.db")
    
    methods = dir(sw)
    assert "calculate_continuity" in methods
    assert "detect_divergence" in methods
    assert "pre_auth_intent" in methods
    assert "track" in methods
    assert "get_profile" in methods
    assert "get_library" in methods
    print("✅ All methods visible in dir()!")


if __name__ == "__main__":
    import asyncio
    
    print("\n" + "="*60)
    print("Testing Shadow Watch Day 1 Refactoring")
    print("="*60 + "\n")
    
    asyncio.run(test_free_tier_no_license_required())
    asyncio.run(test_pro_methods_raise_license_error())
    asyncio.run(test_pro_methods_visible_in_dir())
    
    print("\n" + "="*60)
    print("✅ All Day 1 tests passed!")
    print("="*60 + "\n")
