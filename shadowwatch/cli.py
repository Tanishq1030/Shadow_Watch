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

async def list_divergences(sw: ShadowWatch, unresolved_only: bool = False):
    """List recent global divergence events"""
    status_str = " (Unresolved Only)" if unresolved_only else ""
    print(f"\n🚨 Recent Global Divergences{status_str}")
    print("=" * 80)
    
    async with sw.AsyncSessionLocal() as db:
        from sqlalchemy import text as sa_text
        query = "SELECT id, user_id, mode, magnitude, detected_at, resolved_at FROM divergence_events"
        if unresolved_only:
            query += " WHERE resolved_at IS NULL"
        query += " ORDER BY detected_at DESC LIMIT 20"
        
        result = await db.execute(sa_text(query))
        events = result.mappings().all()
        
        if not events:
            print("   (No recorded divergence events)")
            return
            
        print(f"{'ID':<6} {'TIMESTAMP':<20} {'USER_ID':<15} {'MODE':<10} {'MAG':<6} {'STATUS'}")
        print("-" * 80)
        for ev in events:
            status = "🔴 ACTIVE" if not ev['resolved_at'] else "🟢 RESOLVED"
            ts = str(ev['detected_at'])[:19]
            print(f"{ev['id']:<6} {ts:<20} {ev['user_id']:<15} {ev['mode']:<10} {ev['magnitude']:<6.2f} {status}")

async def resolve_event(sw: ShadowWatch, event_id: int, resolution: str, notes: str):
    """Resolve a specific divergence event"""
    print(f"\n✅ Resolving Event {event_id} as {resolution}...")
    res = await sw.resolve_divergence(event_id, resolution, notes)
    if res.get("success"):
        print(f"✨ Successfully resolved event {event_id} for user {res['user_id']}")
    else:
        print(f"❌ Error: {res.get('error')}")

async def show_stats(sw: ShadowWatch):
    """Show global system metrics"""
    print("\n📊 Shadow Watch System Stats")
    print("=" * 50)
    stats = await sw.get_system_stats()
    print(f"Total Monitored Users:  {stats['total_monitored_users']}")
    print(f"Unresolved Alerts:      {stats['unresolved_alerts']}")
    last_act = stats['last_system_activity']
    print(f"Last System Activity:   {str(last_act)[:19] if last_act else 'N/A'}")

def main():
    parser = argparse.ArgumentParser(description="Shadow Watch Admin CLI")
    parser.add_argument("--db-url", help="PostgreSQL connection string")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # stats
    subparsers.add_parser("stats", help="Show global system metrics")
    
    # inspect-user
    inspect_parser = subparsers.add_parser("inspect-user", help="Inspect a specific user")
    inspect_parser.add_argument("user_id", help="The user ID to inspect")
    
    # events (was list-divergences)
    events_parser = subparsers.add_parser("events", help="List recent divergence events")
    events_parser.add_argument("--unresolved", action="store_true", help="Show only unresolved events")
    
    # resolve
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a divergence event")
    resolve_parser.add_argument("event_id", type=int, help="The ID of the event to resolve")
    resolve_parser.add_argument("--type", required=True, 
                                choices=['false_positive', 'legitimate_change', 'confirmed_attack', 'user_verified'],
                                help="The resolution type")
    resolve_parser.add_argument("--notes", default="", help="Optional notes for resolution")
    
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
    
    if args.command == "stats":
        asyncio.run(show_stats(sw))
    elif args.command == "inspect-user":
        asyncio.run(inspect_user(sw, args.user_id))
    elif args.command == "events":
        asyncio.run(list_divergences(sw, args.unresolved))
    elif args.command == "resolve":
        asyncio.run(resolve_event(sw, args.event_id, args.type, args.notes))

if __name__ == "__main__":
    main()
