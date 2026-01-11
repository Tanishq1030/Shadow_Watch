"""
Shadow Watch - E-commerce Example

Track product views, cart additions, purchases.
Build user interest profiles for product recommendations.
"""

import asyncio
from shadowwatch import ShadowWatch
from shadowwatch.models import Base


async def main():
    print("Shadow Watch - E-commerce Example\n")
    
    # Initialize Shadow Watch (local dev mode, no license)
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./ecommerce_demo.db",
        license_key=None  # Local dev mode - 1000 events free
    )
    
    # Initialize database
    await sw.init_database()
    
    user_id = 123
    
    # Scenario: User browses products
    print("📱 User browsing products...")
    await sw.track(user_id=user_id, entity_id="laptop_dell_xps_15", action="view")
    await sw.track(user_id=user_id, entity_id="mouse_logitech_mx", action="view")
    await sw.track(user_id=user_id, entity_id="keyboard_mechanical", action="view")
    print("   ✓ Tracked 3 product views\n")
    
    # User adds to cart
    print("🛒 User adds items to cart...")
    await sw.track(user_id=user_id, entity_id="laptop_dell_xps_15", action="add_to_cart")
    await sw.track(user_id=user_id, entity_id="mouse_logitech_mx", action="add_to_cart")
    print("   ✓ Tracked 2 cart additions\n")
    
    # User completes purchase
    print("💳 User completes purchase...")
    await sw.track(
        user_id=user_id,
        entity_id="laptop_dell_xps_15",
        action="purchase",
        metadata={
            "price": 1299.99,
            "quantity": 1,
            "payment_method": "credit_card"
        }
    )
    await sw.track(
        user_id=user_id,
        entity_id="mouse_logitech_mx",
        action="purchase",
        metadata={
            "price": 79.99,
            "quantity": 1
        }
    )
    print("   ✓ Tracked 2 purchases\n")
    
    # Get user profile for recommendations
    print("🎯 Building user profile...")
    profile = await sw.get_profile(user_id=user_id)
    
    print(f"\nUser Interest Profile:")
    print(f"  Total items tracked: {profile['total_items']}")
    print(f"\n  Top interests:")
    for i, item in enumerate(profile['library'][:5], 1):
        print(f"    {i}. {item['entity_id']} (score: {item['score']:.2f})")
    
    print("\n💡 Recommendation Strategy:")
    print("  - User interested in: laptops, computer accessories")
    print("  - Recommend: laptop bags, USB hubs, monitors")
    print("  - Cross-sell: warranty, premium support")
    
    print(f"\n✅ E-commerce tracking complete!")
    print(f"   Events used: {sw._event_count}/{sw._event_limit}")


if __name__ == "__main__":
    asyncio.run(main())
