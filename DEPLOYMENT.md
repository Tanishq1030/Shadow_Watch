# Shadow Watch Production Deployment Guide

## ⚠️ Critical: Multi-Instance Caching

**If you deploy Shadow Watch across multiple instances (load balancer, Kubernetes, etc.), you MUST use Redis for shared caching.**

### The Problem

Without shared cache, each app instance has its own separate cache:

```
Load Balancer
    │
    ├──▶ Instance 1 (cache: fingerprint=abc123)
    ├──▶ Instance 2 (cache: fingerprint=xyz789)  ❌ INCONSISTENT!
    └──▶ Instance 3 (cache: fingerprint=???)
```

**This causes:**
- ❌ Stale license verification
- ❌ Inconsistent behavioral fingerprints
- ❌ Different trust scores for same user
- ❌ Wasted memory (3x duplication)

---

## ✅ Solution: Redis for Shared Cache

### Single Instance (Development)

```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="postgresql://...",
    license_key="SW-TRIAL-XXXX-..."
    # redis_url not provided → uses in-memory cache (OK for single instance)
)
```

### Multi-Instance (Production)

```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="postgresql://...",
    license_key="SW-PROD-XXXX-...",
    redis_url="redis://localhost:6379"  # ✅ REQUIRED for production!
)
```

---

## Redis Setup

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

### 3. Update Shadow Watch Initialization

**Install Shadow Watch with Redis support:**
```bash
# Basic installation (development, single-instance)
pip install shadowwatch

# Production installation (multi-instance with Redis)
pip install shadowwatch[redis]
```

**Initialize with Redis:**
```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="postgresql://...",
    license_key="SW-PROD-XXXX-...",
    redis_url="redis://localhost:6379"
)
```

---

## Deployment Architectures

### Architecture 1: Single Server (No Redis Needed)

```
┌─────────────────────┐
│   App Server        │
│   (1 instance)      │
│                     │
│   ShadowWatch       │
│   MemoryCache ✓     │
└─────────────────────┘
```

**Config:**
```python
sw = ShadowWatch(
    database_url="...",
    license_key="...",
    # redis_url not provided → MemoryCache
)
```

---

### Architecture 2: Load-Balanced (Redis Required)

```
┌─────────────────────────────────┐
│       Load Balancer             │
└─────────────────────────────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ App 1   │ │ App 2   │ │ App 3   │
│ SW+Redis│ │ SW+Redis│ │ SW+Redis│
└─────────┘ └─────────┘ └─────────┘
    │         │            │
    └─────────┴────────────┘
              │
         ┌────▼────────┐
         │    Redis    │
         │  (shared)   │
         └─────────────┘
```

**Config:**
```python
sw = ShadowWatch(
    database_url="...",
    license_key="...",
    redis_url="redis://redis-server:6379"  # ✅ REQUIRED
)
```

---

### Architecture 3: Kubernetes (Redis Required)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shadowwatch-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: your-app:latest
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

**Config:**
```python
import os

sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    license_key=os.getenv("SHADOWWATCH_LICENSE"),
    redis_url=os.getenv("REDIS_URL")  # ✅ From environment
)
```

---

## What Gets Cached?

Shadow Watch caches:

1. **License Verification** (24 hours)
   - Cache key: `shadowwatch:license:{license_key}`
   - Reduces API calls to license server

2. **Behavioral Fingerprints** (future enhancement)
   - Cache key: `shadowwatch:fingerprint:{user_id}`
   - Speeds up trust score calculation

3. **User Profiles** (future enhancement)
   - Cache key: `shadowwatch:profile:{user_id}`
   - Reduces database queries

---

## Cache Configuration

### Default TTLs

- License verification: 24 hours (86400 seconds)
- Fingerprints: 1 hour (3600 seconds)
- User profiles: 5 minutes (300 seconds)

### Custom TTLs (Advanced)

```python
# In your application code
await sw.cache.set(
    "custom:key",
    {"data": "value"},
    ttl_seconds=1800  # 30 minutes
)
```

---

## Monitoring

### Redis Memory Usage

```bash
redis-cli info memory
```

### Cache Hit Rate

```bash
redis-cli info stats | grep keyspace
```

### Shadow Watch Cache Keys

```bash
redis-cli keys "shadowwatch:*"
```

---

## Troubleshooting

### Issue: "Connection refused" to Redis

**Cause:** Redis not running or wrong URL

**Fix:**
```bash
# Check Redis is running
redis-cli ping

# Check Redis URL in code
redis_url="redis://localhost:6379"  # Correct
redis_url="redis://127.0.0.1:6379"  # Also works
```

### Issue: Caches not sharing across instances

**Cause:** Each instance using MemoryCache (redis_url not provided)

**Fix:**
```python
# WRONG (each instance has separate cache)
sw = ShadowWatch(database_url="...", license_key="...")

# CORRECT (shared cache)
sw = ShadowWatch(
    database_url="...",
    license_key="...",
    redis_url="redis://localhost:6379"  # ✅ Add this!
)
```

---

## Performance Impact

### With Redis (Production)

- License verification: 1-2ms (cached)
- Trust score calculation: 5-10ms (cached fingerprints)
- Database queries: Only on cache miss

### Without Redis (Development)

- License verification: 100-200ms (API call every time)
- Trust score calculation: 50-100ms (DB queries every time)

**Conclusion:** Redis provides 10-20x performance improvement.

---

## Security

### Redis Authentication

**Production setup:**
```bash
# redis.conf
requirepass your-strong-password
```

**Shadow Watch config:**
```python
sw = ShadowWatch(
    database_url="...",
    license_key="...",
    redis_url="redis://:your-strong-password@localhost:6379"
)
```

### Redis TLS

**For production:**
```python
sw = ShadowWatch(
    database_url="...",
    license_key="...",
    redis_url="rediss://your-redis-host:6380"  # rediss = TLS
)
```

---

## Summary

✅ **Single instance:** No Redis needed (MemoryCache is fine)  
✅ **Multi-instance:** Redis REQUIRED (shared cache)  
✅ **Production:** Always use Redis + authentication  
✅ **Development:** MemoryCache is OK  

**Bottom line:** If you have more than 1 app instance, use Redis.
