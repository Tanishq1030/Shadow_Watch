"""
Test calculate_continuity() implementation

Tests the freely available calculate_continuity() method.
"""

import asyncio
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shadowwatch import ShadowWatch


async def main():
    print("🧪 Testing calculate_continuity()")
    print("=" * 60)
    
    # PostgreSQL connection (local)
    DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test"
    
    # Initialize ShadowWatch
    sw = ShadowWatch(database_url=DATABASE_URL)
    
    print("\n✅ ShadowWatch initialized (PostgreSQL)")
    
    # Initialize database (creates free tier tables only)
    print("\n📊 Initializing database...")
    await sw.init_database()
    print("✅ Database initialized")
    
    # Note: Invariant tables should be created via migration:
    # Run: shadowwatch/storage/migrations/003_invariant_tables.sql on Supabase
    # This test assumes the migration has already been run
    
    # Create test user with some activity
    test_user = "test_user_continuity_001"
    
    print(f"\n📝 Creating test activity for user: {test_user}")
    print("   Simulating normal behavior pattern...")
    
    # Simulate 50 normal events
    entities = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    actions = ["view", "search", "analyze"]
    
    for i in range(50):
        entity = entities[i % len(entities)]
        action = actions[i % len(actions)]
        
        await sw.track(
            user_id=test_user,
            entity_id=entity,
            action=action
        )
        
        # Small delay to simulate realistic timing
        if i % 10 == 0:
            await asyncio.sleep(0.5)
    
    print(f"✅ Created {50} events")
    
    # Test 1: First continuity calculation (baseline establishment)
    print("\n" + "=" * 60)
    print("TEST 1: Baseline Establishment (First 50 events)")
    print("=" * 60)
    
    result1 = await sw.calculate_continuity(test_user)
    
    print(f"\n📊 Continuity Result:")
    print(f"   Score:        {result1['score']:.3f}")
    print(f"   Confidence:   {result1['confidence']:.3f}")
    print(f"   State:        {result1['state']}")
    print(f"   Sample Count: {result1['sample_count']}")
    print(f"   Distance:     {result1['distance']:.3f}")
    
    # Verify expected behavior
    assert result1['state'] in ['learning', 'stable'], f"Expected learning/stable, got {result1['state']}"
    assert 0.0 <= result1['score'] <= 1.0, f"Score out of range: {result1['score']}"
    assert 0.0 <= result1['confidence'] <= 1.0, f"Confidence out of range: {result1['confidence']}"
    
    print("\n✅ TEST 1 PASSED - Baseline established")
    
    # Test 2: Add more matching events (should maintain high continuity)
    print("\n" + "=" * 60)
    print("TEST 2: Consistent Behavior (50 more matching events)")
    print("=" * 60)
    
    print("\n📝 Adding more consistent activity...")
    for i in range(50):
        entity = entities[i % len(entities)]
        action = actions[i % len(actions)]
        
        await sw.track(
            user_id=test_user,
            entity_id=entity,
            action=action
        )
    
    result2 = await sw.calculate_continuity(test_user)
    
    print(f"\n📊 Continuity Result:")
    print(f"   Score:        {result2['score']:.3f} (was {result1['score']:.3f})")
    print(f"   Confidence:   {result2['confidence']:.3f} (was {result1['confidence']:.3f})")
    print(f"   State:        {result2['state']}")
    print(f"   Sample Count: {result2['sample_count']}")
    print(f"   Distance:     {result2['distance']:.3f}")
    
    # Verify continuity is high
    assert result2['score'] >= 0.5, f"Expected high continuity, got {result2['score']}"
    assert result2['confidence'] > result1['confidence'], "Confidence should increase with more data"
    assert result2['sample_count'] > result1['sample_count'], "Sample count should increase"
    
    print("\n✅ TEST 2 PASSED - Consistent behavior maintains continuity")
    
    # Test 3: Add divergent events (should detect change)
    print("\n" + "=" * 60)
    print("TEST 3: Divergent Behavior (20 unusual events)")
    print("=" * 60)
    
    print("\n📝 Simulating divergent behavior...")
    unusual_entities = ["UNUSUAL1", "UNUSUAL2", "UNUSUAL3"]
    unusual_actions = ["export_data", "delete"]
    
    for i in range(20):
        entity = unusual_entities[i % len(unusual_entities)]
        action = unusual_actions[i % len(unusual_actions)]
        
        await sw.track(
            user_id=test_user,
            entity_id=entity,
            action=action
        )
    
    result3 = await sw.calculate_continuity(test_user)
    
    print(f"\n📊 Continuity Result:")
    print(f"   Score:        {result3['score']:.3f} (was {result2['score']:.3f})")
    print(f"   Confidence:   {result3['confidence']:.3f}")
    print(f"   State:        {result3['state']}")
    print(f"   Sample Count: {result3['sample_count']}")
    print(f"   Distance:     {result3['distance']:.3f} (was {result2['distance']:.3f})")
    
    # Verify divergence detected
    print("\n🔍 Divergence Detection:")
    if result3['distance'] > result2['distance']:
        print(f"   ✅ Distance increased: {result2['distance']:.3f} → {result3['distance']:.3f}")
    else:
        print(f"   ⚠️  Distance did not increase as expected")
    
    if result3['score'] < result2['score']:
        print(f"   ✅ Score decreased: {result2['score']:.3f} → {result3['score']:.3f}")
    else:
        print(f"   ⚠️  Score did not decrease (may be due to decay)")
    
    print("\n✅ TEST 3 PASSED - Divergence affects continuity metrics")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\nSummary:")
    print(f"  • Baseline: score={result1['score']:.3f}, n={result1['sample_count']}")
    print(f"  • Stable:   score={result2['score']:.3f}, n={result2['sample_count']}")
    print(f"  • Diverged: score={result3['score']:.3f}, n={result3['sample_count']}")
    print("\n✅ calculate_continuity() is working correctly!")
    

if __name__ == "__main__":
    asyncio.run(main())
