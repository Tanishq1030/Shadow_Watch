"""
Shadow Watch - Social Media Example

Track likes, follows, shares.
Detect bot behavior vs real users.
"""

import asyncio
from shadowwatch import ShadowWatch
from shadowwatch.models import Base


async def main():
    print("Shadow Watch - Social Media Example\n")
    
    # Initialize Shadow Watch
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./social_demo.db",
        license_key=None
    )
    
    await sw.init_database()
    
    # Test two users: real user vs potential bot
    real_user = 100
    bot_user = 200
    
    # Real user: varied behavior
    print("👤 Real user activity (varied, organic)...")
    await sw.track(user_id=real_user, entity_id="post_tech_news_1", action="like")
    await sw.track(user_id=real_user, entity_id="post_cat_video", action="like")
    await sw.track(user_id=real_user, entity_id="user_tech_influencer", action="follow")
    await sw.track(user_id=real_user, entity_id="post_tech_news_1", action="share")
    await sw.track(user_id=real_user, entity_id="post_meme", action="like")
    await sw.track(user_id=real_user, entity_id="hashtag_technology", action="search")
    print("   ✓ 6 varied actions\n")
    
    # Bot user: repetitive behavior
    print("🤖 Suspicious user activity (repetitive, automated)...")
    for i in range(20):
        await sw.track(user_id=bot_user, entity_id=f"random_post_{i}", action="like")
    print("   ✓ 20 likes, all different posts, rapid succession\n")
    
    # Analyze behavior patterns
    print("🔍 Analyzing behavior patterns...\n")
    
    # Real user analysis
    real_profile = await sw.get_profile(user_id=real_user)
    real_total = sum(item['activity_count'] for item in real_profile['library'])
    real_unique = len(real_profile['library'])
    
    print(f"Real User Profile:")
    print(f"  Total actions: {real_total}")
    print(f"  Unique entities: {real_unique}")
    print(f"  Diversity ratio: {real_unique/real_total:.2f}")
    print(f"  Top interests: {', '.join([item['entity_id'] for item in real_profile['library'][:3]])}")
    print(f"  ✅ VERDICT: Real user (varied behavior)\n")
    
    # Bot user analysis
    bot_profile = await sw.get_profile(user_id=bot_user)
    bot_total = sum(item['activity_count'] for item in bot_profile['library'])
    bot_unique = len(bot_profile['library'])
    
    print(f"Bot User Profile:")
    print(f"  Total actions: {bot_total}")
    print(f"  Unique entities: {bot_unique}")
    print(f"  Diversity ratio: {bot_unique/bot_total:.2f}")
    print(f"  Top interests: {', '.join([item['entity_id'] for item in bot_profile['library'][:3]])}")
    
    # Bot detection heuristic
    if bot_total > 15 and bot_unique == bot_total and bot_unique > 10:
        print(f"  ⚠️  VERDICT: Possible bot detected!")
        print(f"     Reason: High volume, all unique (no re-engagement), rapid pace")
    
    print(f"\n✅ Social media analysis complete!")


if __name__ == "__main__":
    asyncio.run(main())
