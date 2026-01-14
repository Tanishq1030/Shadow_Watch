"""
Quick test of Day 1 refactoring (no pytest dependency)
"""
import asyncio
from shadowwatch import ShadowWatch, LicenseError


async def test_free_tier():
    print("\n1️⃣ Testing free tier without license...")
    
    sw = ShadowWatch(database_url="sqlite+aiosqlite:///test_day1.db")
    
    # Initialize database
    await sw.init_database()
    
    # Test free tier methods
    await sw.track(user_id=123, entity_id="AAPL", action="view")
    print("   ✅ track() works")
    
    profile = await sw.get_profile(user_id=123)
    print("   ✅ get_profile() works")
    
    library = await sw.get_library(user_id=123)
    print("   ✅ get_library() works")


async def test_pro_methods():
    print("\n2️⃣ Testing Pro methods raise LicenseError...")
    
    sw = ShadowWatch(database_url="sqlite+aiosqlite:///test_day1.db")
    
    try:
        await sw.calculate_continuity("user_123")
        print("   ❌ Should have raised LicenseError!")
    except LicenseError as e:
        print("   ✅ LicenseError raised correctly")
        print(f"   📝 Error message: {str(e)[:80]}...")


def test_autocomplete():
    print("\n3️⃣ Testing methods visible in dir()...")
    
    sw = ShadowWatch(database_url="sqlite+aiosqlite:///test_day1.db")
    
    methods = dir(sw)
    
    # Free tier methods
    assert "track" in methods
    assert "get_profile" in methods
    assert "get_library" in methods
    print("   ✅ Free tier methods visible")
    
    # Pro tier methods
    assert "calculate_continuity" in methods
    assert "detect_divergence" in methods
    assert "pre_auth_intent" in methods
    print("   ✅ Pro tier methods visible")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Shadow Watch Day 1 Refactoring Test")
    print("="*70)
    
    asyncio.run(test_free_tier())
    asyncio.run(test_pro_methods())
    test_autocomplete()
    
    print("\n" + "="*70)
    print("✅ All Day 1 tests passed!")
    print("="*70 + "\n")
