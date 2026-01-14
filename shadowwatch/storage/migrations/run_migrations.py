"""
Run Shadow Watch Database Migrations

Usage:
    python -m shadowwatch.storage.migrations.run_migrations <database_url>

Example:
    python -m shadowwatch.storage.migrations.run_migrations "postgresql://localhost/shadowwatch"
"""
import asyncio
import sys
from pathlib import Path
import asyncpg


async def run_migrations(database_url: str):
    """
    Run all SQL migrations in order
    
    Args:
        database_url: PostgreSQL connection string
    """
    print("\n" + "="*70)
    print("Shadow Watch Database Migrations")
    print("="*70 + "\n")
    
    # Connect to database
    try:
        conn = await asyncpg.connect(database_url)
        print(f"✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    # Find migration files
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("⚠️  No migration files found")
        await conn.close()
        return
    
    print(f"📁 Found {len(migration_files)} migration file(s)\n")
    
    # Run each migration
    for migration_file in migration_files:
        try:
            print(f"🔄 Running {migration_file.name}...")
            
            sql = migration_file.read_text()
            await conn.execute(sql)
            
            print(f"   ✅ {migration_file.name} complete")
        except Exception as e:
            print(f"   ❌ {migration_file.name} failed: {e}")
            await conn.close()
            sys.exit(1)
    
    await conn.close()
    
    print("\n" + "="*70)
    print("✅ All migrations complete!")
    print("="*70 + "\n")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_migrations.py <database_url>")
        print("\nExample:")
        print('  python run_migrations.py "postgresql://localhost/shadowwatch"')
        sys.exit(1)
    
    database_url = sys.argv[1]
    asyncio.run(run_migrations(database_url))


if __name__ == "__main__":
    main()
