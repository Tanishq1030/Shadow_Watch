"""
Shadow Watch Admin CLI

Observability tool for inspecting user state and behavioral divergences.
"""
import asyncio
import argparse
import sys
import json
from datetime import datetime
from sqlalchemy import select, text
from shadowwatch import ShadowWatch

async def inspect_user(sw: ShadowWatch, user_id: str):
    """Show behavioral state for a specific user"""
    print(f"\n🔍 Inspecting User: {user_id}")
    print("=" * 60)
    
    async with sw.AsyncSessionLocal() as db:
        # 1. Invariant State
        from sqlalchemy import text as sa_text
        result = await db.execute(sa_text(
            "SELECT * FROM invariant_state WHERE user_id = :u"
        ), {"u": user_id})
        state = result.mappings().first()
        
        if not state:
            print(f"❌ No invariant state found for user {user_id}")
            return
            
        print(f"📊 CONTINUITY")
        print(f"   Score:      {state['continuity_score']:.3f}")
        print(f"   Confidence: {state['continuity_confidence']:.3f}")
        print(f"   Samples:    {state['sample_count']}")
        print(f"   Last Seen:  {state['last_seen_at']}")
        
        print(f"\n📈 DIVERGENCE")
        print(f"   Mode:       {state['divergence_mode'] or 'None'}")
        print(f"   Accumulated: {state['divergence_accumulated']:.3f}")
        print(f"   Velocity:    {state['divergence_velocity']:.3f}")
        
        # 2. Recent Divergence Events
        print(f"\n🚨 RECENT EVENTS")
        event_res = await db.execute(sa_text(
            "SELECT mode, magnitude, detected_at FROM divergence_events "
            "WHERE user_id = :u ORDER BY detected_at DESC LIMIT 5"
        ), {"u": user_id})
        events = event_res.mappings().all()
        
        if not events:
            print("   (No recorded divergence events)")
        for ev in events:
            print(f"   [{ev['detected_at']}] {ev['mode'].upper()} (mag={ev['magnitude']:.2f})")

async def list_divergences(sw: ShadowWatch):
    """List recent global divergence events"""
    print("\n🚨 Recent Global Divergences")
    print("=" * 60)
    
    async with sw.AsyncSessionLocal() as db:
        from sqlalchemy import text as sa_text
        result = await db.execute(sa_text(
            "SELECT user_id, mode, magnitude, detected_at FROM divergence_events "
            "ORDER BY detected_at DESC LIMIT 20"
        ))
        events = result.mappings().all()
        
        if not events:
            print("   (No recorded divergence events)")
            return
            
        print(f"{'TIMESTAMP':<25} {'USER_ID':<20} {'MODE':<10} {'MAG'}")
        print("-" * 60)
        for ev in events:
            print(f"{str(ev['detected_at'])[:19]:<25} {ev['user_id']:<20} {ev['mode']:<10} {ev['magnitude']:.2f}")

def main():
    parser = argparse.ArgumentParser(description="Shadow Watch Admin CLI")
    parser.add_argument("--db-url", help="PostgreSQL connection string")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # inspect-user
    inspect_parser = subparsers.add_parser("inspect-user", help="Inspect a specific user")
    inspect_parser.add_argument("user_id", help="The user ID to inspect")
    
    # list-divergences
    subparsers.add_parser("list-divergences", help="List recent divergence events")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    import os
    db_url = args.db_url or os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL not set and --db-url not provided.")
        sys.exit(1)
        
    sw = ShadowWatch(database_url=db_url)
    
    if args.command == "inspect-user":
        asyncio.run(inspect_user(sw, args.user_id))
    elif args.command == "list-divergences":
        asyncio.run(list_divergences(sw))

if __name__ == "__main__":
    main()
