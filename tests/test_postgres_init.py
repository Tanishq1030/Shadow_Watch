"""
Test Shadow Watch Database Initialization

Run this to verify table creation works with PostgreSQL
"""

import asyncio
from shadowwatch import ShadowWatch


async def test_database_init():
    print("=" * 70)
    print("TESTING SHADOW WATCH DATABASE INITIALIZATION")
    print("=" * 70)
    
    # Initialize Shadow Watch with PostgreSQL
    # Replace with your actual connection string
    DATABASE_URL = input("\nEnter PostgreSQL URL (or press Enter for default): ").strip()
    if not DATABASE_URL:
        DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/shadowwatch_test"
    
    print(f"\n📡 Connecting to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    sw = ShadowWatch(
        database_url=DATABASE_URL,
        license_key=None  # Local dev mode
    )
    
    print("\n🔧 Calling init_database()...")
    
    try:
        await sw.init_database()
        print("✅ init_database() completed without errors")
    except Exception as e:
        print(f"❌ init_database() failed: {e}")
        return
    
    # Check if tables exist
    print("\n📊 Checking if tables were created...")
    
    from sqlalchemy import text
    async with sw.engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'shadow_watch%'
            ORDER BY tablename
        """))
        
        tables = [row[0] for row in result]
        
        if tables:
            print(f"\n✅ Found {len(tables)} Shadow Watch tables:")
            for table in tables:
                print(f"   • {table}")
        else:
            print("\n❌ NO Shadow Watch tables found!")
            print("   This means init_database() didn't create tables.")
    
    # Try tracking an event
    print("\n📝 Testing event tracking...")
    
    try:
        await sw.track(
            user_id=999,
            entity_id="TEST_SYMBOL",
            action="view",
            metadata={"test": True}
        )
        print("✅ Event tracking successful!")
    except Exception as e:
        print(f"❌ Event tracking failed: {e}")
    
    # Try getting profile
    print("\n👤 Testing profile retrieval...")
    
    try:
        profile = await sw.get_profile(user_id=999)
        print(f"✅ Profile retrieved: {profile['total_items']} items")
    except Exception as e:
        print(f"❌ Profile retrieval failed: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_database_init())
