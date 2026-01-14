"""
Database Connection Management

Async PostgreSQL/CockroachDB connection pool.
"""

import os
import asyncpg
from contextlib import asynccontextmanager

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/shadowwatch")

# Connection pool (singleton)
_pool = None


async def get_pool():
    """Get database connection pool (singleton)"""
    global _pool
    
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=5.0
        )
    
    return _pool


@asynccontextmanager
async def get_db():
    """
    Get database connection from pool
    
    Usage:
        async with get_db() as db:
            await db.execute("...")
    """
    pool = await get_pool()
    
    async with pool.acquire() as connection:
        yield connection


async def close_pool():
    """Close database pool (on shutdown)"""
    global _pool
    
    if _pool:
        await _pool.close()
        _pool = None
