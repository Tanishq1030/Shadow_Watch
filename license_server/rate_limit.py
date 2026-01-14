"""
Rate Limiting - Redis-Backed

Protect infrastructure with clean, deterministic rate limits.
"""

from fastapi import Request, HTTPException
from typing import Optional
import json

from .kv_store import redis


class RateLimiter:
    """
    Redis-backed rate limiter
    
    Strategy:
    - Counter per (endpoint, identifier) pair
    - TTL = window duration
    - Atomic INCR for race-safety
    """
    
    # Rate limit buckets
    LIMITS = {
        "license_validate": {"limit": 60, "window": 60},
        "license_pro": {"limit": 5, "window": 60},
        "license_enterprise": {"limit": 5, "window": 60},
        "license_revoke": {"limit": 5, "window": 60},
        "admin": {"limit": 20, "window": 60},
    }
    
    @staticmethod
    async def check(
        request: Request,
        endpoint: str,
        identifier: Optional[str] = None
    ):
        """
        Check rate limit for endpoint + identifier
        
        Args:
            request: FastAPI request
            endpoint: Endpoint key (e.g., "license_validate")
            identifier: Optional identifier (defaults to IP)
        
        Raises:
            HTTPException 429: Rate limit exceeded
        """
        # Get limit config
        config = RateLimiter.LIMITS.get(endpoint)
        
        if not config:
            # No limit configured - allow
            return
        
        limit = config["limit"]
        window = config["window"]
        
        # Default to IP if no identifier
        if not identifier:
            identifier = request.client.host
        
        # Redis key
        redis_key = f"rl:{endpoint}:{identifier}"
        
        # Increment counter
        current = await redis.incr(redis_key)
        
        # Set TTL on first increment
        if current == 1:
            await redis.expire(redis_key, window)
        
        # Check limit
        if current > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {limit}/{window}s"
            )
    
    @staticmethod
    async def check_multi(
        request: Request,
        endpoint: str,
        identifiers: list[str]
    ):
        """
        Check rate limit for multiple identifiers
        
        Useful for checking both IP and license key.
        
        Example:
            await RateLimiter.check_multi(
                request,
                "license_validate",
                [f"ip:{request.client.host}", f"key:{license_key}"]
            )
        """
        for identifier in identifiers:
            await RateLimiter.check(request, endpoint, identifier)
    
    @staticmethod
    async def with_multiplier(
        request: Request,
        endpoint: str,
        identifier: str,
        multiplier: float = 1.0
    ):
        """
        Apply rate limit with multiplier (for Enterprise)
        
        Example:
            # Enterprise gets 5x higher limits
            await RateLimiter.with_multiplier(
                request,
                "license_validate",
                license_key,
                multiplier=5.0
            )
        """
        config = RateLimiter.LIMITS.get(endpoint, {"limit": 60, "window": 60})
        
        effective_limit = int(config["limit"] * multiplier)
        window = config["window"]
        
        redis_key = f"rl:{endpoint}:{identifier}"
        
        current = await redis.incr(redis_key)
        
        if current == 1:
            await redis.expire(redis_key, window)
        
        if current > effective_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {effective_limit}/{window}s"
            )


# Convenience functions for common patterns

async def rate_limit_ip(request: Request, endpoint: str):
    """Rate limit by IP only"""
    await RateLimiter.check(request, endpoint)


async def rate_limit_ip_and_key(request: Request, endpoint: str, key: str):
    """Rate limit by both IP and license key"""
    await RateLimiter.check_multi(
        request,
        endpoint,
        [f"ip:{request.client.host}", f"key:{key}"]
    )
