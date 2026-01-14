"""
Database connection for License Server (Vercel Serverless)

Uses Supabase client instead of asyncpg because:
- Vercel serverless can't maintain connection pools
- Supabase client handles connections per request
- Works reliably in serverless environments
"""
import os
from supabase import create_client, Client
from typing import Optional

# Initialize Supabase client (singleton)
_supabase: Optional[Client] = None


def get_supabase() -> Client:
    """
    Get or create Supabase client
    
    Singleton pattern to reuse client across requests
    """
    global _supabase
    
    if _supabase is None:
        _supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    return _supabase


async def get_db():
    """
    Get database client for license operations
    
    Returns Supabase client (not asyncpg pool)
    """
    return get_supabase()


async def close_pool():
    """No-op for compatibility (Supabase client doesn't need cleanup)"""
    pass
