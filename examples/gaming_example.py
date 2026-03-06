"""
Shadow Watch - Gaming Example

Track character selection, level progression, item usage.
Recommend in-game items based on playstyle.
"""

import asyncio
from shadowwatch import ShadowWatch
from shadowwatch.models import Base


async def main():
    print("Shadow Watch - Gaming Example\n")
    
    # Initialize Shadow Watch
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./gaming_demo.db",
    )
    
    await sw.init_database()
    
    user_id = 123
    
    # Game session start
    print("🎮 Player starts new session...")
    
    # Character selection
    print("\n⚔️  Character selection...")
    await sw.track(user_id=user_id, entity_id="character_warrior", action="select")
    print("   ✓ Selected: Warrior class\n")
    
    # Gameplay tracking
    print("🗺️  Gameplay progression...")
    await sw.track(
        user_id=user_id,
        entity_id="level_1_forest",
        action="complete",
        metadata={"time_taken": 120, "deaths": 0}
    )
    await sw.track(
        user_id=user_id,
        entity_id="level_2_cave",
        action="complete",
        metadata={"time_taken": 180, "deaths": 1}
    )
    await sw.track(
        user_id=user_id,
        entity_id="level_3_boss",
        action="complete",
        metadata={"time_taken": 300, "deaths": 3}
    )
    print("   ✓ Completed 3 levels\n")
    
    # Item/equipment usage
    print("⚔️  Equipment usage...")
    await sw.track(user_id=user_id, entity_id="weapon_greatsword", action="equip")
    await sw.track(user_id=user_id, entity_id="armor_heavy_plate", action="equip")
    await sw.track(user_id=user_id, entity_id="potion_health_large", action="use")
    await sw.track(user_id=user_id, entity_id="skill_berserk_rage", action="use")
    print("   ✓ Used 4 items/skills\n")
    
    # Analyze playstyle
    print("📊 Analyzing playstyle...")
    profile = await sw.get_profile(user_id=user_id)
    
    interests = {item['entity_id']: item['score'] for item in profile['library']}
    
    print(f"\nPlayer Profile:")
    print(f"  Preferred class: Warrior")
    print(f"  Combat style: Melee/Tank (greatsword, heavy armor)")
    print(f"  Skill usage: Aggressive (berserk rage)")
    
    # Generate recommendations
    print(f"\n💎 Recommended Items:")
    
    if 'character_warrior' in interests:
        recommendations = [
            "🗡️  Legendary Greatsword (+50 damage)",
            "🛡️  Titan's Plate Armor (+100 defense)",
            "💪 Strength Potion (+25% damage)",
            "⚡ Rage Enhancement (+30% berserk duration)"
        ]
        for rec in recommendations:
            print(f"  {rec}")
    
    print(f"\n📈 Progression tracking:")
    print(f"  Levels completed: 3")
    print(f"  Average clear time: 200 seconds")
    print(f"  Death count: 4 (normal difficulty)")
    
    print(f"\n✅ Gaming session tracked!")
    print(f"   Events used: {sw._event_count}/{sw._event_limit}")


if __name__ == "__main__":
    asyncio.run(main())
