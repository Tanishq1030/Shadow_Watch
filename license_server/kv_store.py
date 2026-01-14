"""
KV Store - Redis Wrapper

Simplified Redis interface for caching and rate limiting.
"""

import os
import json
from typing import Optional, Any
import redis.asyncio as aioredis  # Changed alias to avoid conflict

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create async Redis client
_redis_client = None


async def get_redis():
    """Get Redis client (singleton)"""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = aioredis.from_url(  # Use aioredis alias
            REDIS_URL,
            decode_responses=True,
            encoding="utf-8"
        )
    
    return _redis_client


class RedisKV:
    """
    Redis key-value store wrapper
    
    Provides simplified async interface for common operations.
    """
    
    @staticmethod
    async def get(key: str) -> Optional[str]:
        """Get value by key"""
        client = await get_redis()
        return await client.get(key)
    
    @staticmethod
    async def set(key: str, value: Any, ex: Optional[int] = None):
        """Set value with optional expiration (seconds)"""
        client = await get_redis()
        
        # Serialize if not string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        if ex:
            await client.setex(key, ex, value)
        else:
            await client.set(key, value)
    
    @staticmethod
    async def setex(key: str, seconds: int, value: Any):
        """Set value with expiration"""
        await RedisKV.set(key, value, ex=seconds)
    
    @staticmethod
    async def delete(key: str):
        """Delete key"""
        client = await get_redis()
        await client.delete(key)
    
    @staticmethod
    async def incr(key: str) -> int:
        """Increment counter (atomic)"""
        client = await get_redis()
        return await client.incr(key)
    
    @staticmethod
    async def expire(key: str, seconds: int):
        """Set expiration on existing key"""
        client = await get_redis()
        await client.expire(key, seconds)
    
    @staticmethod
    async def ttl(key: str) -> int:
        """Get TTL for key"""
        client = await get_redis()
        return await client.ttl(key)


# Export singleton instance
redis_kv = RedisKV()
