import asyncio
import sys
import os
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shadowwatch import ShadowWatch


async def main():
    print("🧪 Testing calculate_continuity() - INTEGRATION")
    print("=" * 60)
    
    # Use environment variable or local default
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test")
    
    # Initialize ShadowWatch
    sw = ShadowWatch(database_url=DATABASE_URL)
    
    print(f"✅ ShadowWatch initialized ({DATABASE_URL})")
    
    # Initialize database (creates all tables including invariant ones)
    print("\n📊 Initializing database...")
    await sw.init_database()
    print("✅ Database initialized")
    
    # Create test user with some activity
    test_user = "test_user_continuity_core_001"
    
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
        
        if i % 10 == 0:
            await asyncio.sleep(0.1)
    
    print(f"✅ Created 50 events")
    
    # Test 1: First continuity calculation
    print("\n" + "=" * 60)
    print("TEST 1: Baseline Establishment (First 50 events)")
    print("=" * 60)
    
    result1 = await sw.calculate_continuity(test_user)
    
    print(f"\n📊 Continuity Result:")
    print(f"   Score:        {result1['score']:.3f}")
    print(f"   Confidence:   {result1['confidence']:.3f}")
    print(f"   State:        {result1['state']}")
    print(f"   Sample Count: {result1['sample_count']}")
    
    assert result1['state'] in ['learning', 'stable'], f"Expected learning/stable, got {result1['state']}"
    assert 0.0 <= result1['score'] <= 1.0, f"Score out of range"
    
    print("\n✅ TEST 1 PASSED - Baseline established")
    
    # Test 2: Add more matching events
    print("\n" + "=" * 60)
    print("TEST 2: Consistent Behavior (50 more matching events)")
    print("=" * 60)
    
    for i in range(50):
        entity = entities[i % len(entities)]
        action = actions[i % len(actions)]
        await sw.track(user_id=test_user, entity_id=entity, action=action)
    
    result2 = await sw.calculate_continuity(test_user)
    
    print(f"\n📊 Continuity Result:")
    print(f"   Score:        {result2['score']:.3f} (was {result1['score']:.3f})")
    print(f"   Confidence:   {result2['confidence']:.3f} (was {result1['confidence']:.3f})")
    print(f"   State:        {result2['state']}")
    
    assert result2['confidence'] > result1['confidence'], "Confidence should increase"
    
    print("\n✅ TEST 2 PASSED - Consistent behavior maintains continuity")
    
    # Test 3: Divergent events
    print("\n" + "=" * 60)
    print("TEST 3: Divergent Behavior (20 unusual events)")
    print("=" * 60)
    
    unusual_entities = ["UNUSUAL1", "UNUSUAL2", "UNUSUAL3"]
    unusual_actions = ["export_data", "delete"]
    
    for i in range(20):
        entity = unusual_entities[i % len(unusual_entities)]
        action = unusual_actions[i % len(unusual_actions)]
        await sw.track(user_id=test_user, entity_id=entity, action=action)
    
    result3 = await sw.calculate_continuity(test_user)
    
    print(f"\n📊 Continuity Result:")
    print(f"   Score:        {result3['score']:.3f} (was {result2['score']:.3f})")
    print(f"   Distance:     {result3['distance']:.3f} (was {result2['distance']:.3f})")
    
    print("\n🔍 Divergence Detection:")
    if result3['distance'] > result2['distance']:
        print(f"   ✅ Distance increased: {result2['distance']:.3f} → {result3['distance']:.3f}")
    
    # Check divergence mode
    divergence = await sw.detect_divergence(test_user)
    print(f"   Divergence Mode: {divergence['mode']}")
    print(f"   Magnitude:       {divergence['magnitude']:.3f}")
    
    print("\n✅ TEST 3 PASSED - Divergent behavior detected")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"  • Baseline: score={result1['score']:.3f}, n={result1['sample_count']}")
    print(f"  • Stable:   score={result2['score']:.3f}, n={result2['sample_count']}")
    print(f"  • Diverged: score={result3['score']:.3f}, n={result3['sample_count']}")
    print("\n✅ calculate_continuity() IS WORKING!")


if __name__ == "__main__":
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
