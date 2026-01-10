"""
Shadow Watch Caching Strategy

Handles shared caching across multiple application instances using Redis.
Falls back to in-memory cache for single-instance deployments.
"""

import json
from typing import Optional, Any
from datetime import datetime, timedelta


class CacheBackend:
    """
    Abstract cache backend interface
    
    Implementations:
    - RedisCache (production, multi-instance)
    - MemoryCache (development, single-instance)
    """
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set cached value with TTL (time-to-live)"""
        raise NotImplementedError
    
    async def delete(self, key: str):
        """Delete cached value"""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        raise NotImplementedError


class RedisCache(CacheBackend):
    """
    Redis-backed cache for multi-instance deployments
    
    Usage:
        cache = RedisCache(redis_url="redis://localhost:6379")
        await cache.set("user:123:fingerprint", "abc123", ttl_seconds=3600)
        fp = await cache.get("user:123:fingerprint")
    
    Responsibility:
    - Shared state across multiple app instances
    - Automatic TTL expiration
    - High performance (Redis is fast)
    """
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis = None
    
    async def _get_redis(self):
        """Lazy connection to Redis"""
        if self._redis is None:
            import redis.asyncio as redis
            self._redis = await redis.from_url(self.redis_url, decode_responses=True)
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        redis = await self._get_redis()
        value = await redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        redis = await self._get_redis()
        await redis.setex(key, ttl_seconds, json.dumps(value))
    
    async def delete(self, key: str):
        redis = await self._get_redis()
        await redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        redis = await self._get_redis()
        return await redis.exists(key) > 0


class MemoryCache(CacheBackend):
    """
    In-memory cache for single-instance deployments
    
    ⚠️ WARNING: DO NOT USE IN PRODUCTION WITH MULTIPLE INSTANCES
    
    This is fine for:
    - Local development
    - Single-server deployments
    - Testing
    
    DO NOT USE for:
    - Load-balanced deployments
    - Multi-instance setups
    - Horizontal scaling
    
    Responsibility:
    - Simple caching for development
    - No external dependencies
    - Automatic TTL expiration
    """
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def _is_expired(self, key: str) -> bool:
        if key not in self._expiry:
            return True
        return datetime.utcnow() > self._expiry[key]
    
    async def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        
        if self._is_expired(key):
            await self.delete(key)
            return None
        
        return self._cache[key]
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        self._cache[key] = value
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    async def delete(self, key: str):
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        if self._is_expired(key):
            await self.delete(key)
            return False
        return key in self._cache


def create_cache(redis_url: Optional[str] = None) -> CacheBackend:
    """
    Factory function to create appropriate cache backend
    
    Args:
        redis_url: Redis connection URL (e.g., "redis://localhost:6379")
                  If None, uses in-memory cache
    
    Returns:
        RedisCache if redis_url provided, else MemoryCache
    
    Usage:
        # Production (multi-instance)
        cache = create_cache(redis_url="redis://localhost:6379")
        
        # Development (single-instance)
        cache = create_cache()
    """
    if redis_url:
        return RedisCache(redis_url)
    else:
        return MemoryCache()
