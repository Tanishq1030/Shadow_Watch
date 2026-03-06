# Shadow Watch — Getting Started Guide

## Installation

```bash
pip install shadowwatch
```

With optional extras:

```bash
pip install shadowwatch[redis]          # Redis caching support
pip install shadowwatch[fastapi]        # FastAPI middleware
pip install shadowwatch[redis,fastapi]  # Everything
```

---

## Quick Start (5 Minutes)

### 1. Set Up Your Database

Shadow Watch works with **PostgreSQL** (recommended) or **MySQL**. SQLite is supported for local development only.

**PostgreSQL (production):**

```bash
createdb myapp
```

**SQLite (local dev):**
No setup needed — file is created automatically.

---

### 2. Initialize Shadow Watch

```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="postgresql+asyncpg://user:password@localhost:5432/myapp",
    # redis_url="redis://localhost:6379"  # Optional, for multi-instance caching
)
```

---

### 3. Create Database Tables

```python
await sw.init_database()
```

This creates three tables:

- `shadow_watch_activity_events`
- `shadow_watch_interests`
- `shadow_watch_library_versions`

---

### 4. Track User Activity

```python
# Track a page view
await sw.track(user_id=123, entity_id="AAPL", action="view")

# Track a search
await sw.track(user_id=123, entity_id="TECH_STOCKS", action="search",
               metadata={"query": "tech stocks"})

# Track a trade (highest weight — auto-pins the entity)
await sw.track(user_id=123, entity_id="AAPL", action="trade",
               metadata={"quantity": 10, "price": 185.20})
```

---

### 5. Get User Profile

```python
profile = await sw.get_profile(user_id=123)
print(profile)
# {
#   "total_items": 15,
#   "fingerprint": "a7f9e2c4b8d1...",
#   "library": [
#     {"entity_id": "AAPL", "score": 0.85, "is_pinned": True},
#     {"entity_id": "MSFT", "score": 0.72, "is_pinned": False},
#   ]
# }
```

---

### 6. Verify Login (Behavioral Biometric / ATO Detection)

```python
trust = await sw.verify_login(
    user_id=123,
    request_context={
        "ip": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "device_fingerprint": "abc123...",
    }
)

# {"trust_score": 0.85, "risk_level": "low", "action": "allow"}

if trust["action"] == "allow":
    pass  # proceed
elif trust["action"] == "require_mfa":
    pass  # send 2FA
else:  # block
    pass  # deny + alert
```

---

## FastAPI Integration (Auto-Tracking)

```python
from fastapi import FastAPI
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware

app = FastAPI()

sw = ShadowWatch(database_url="postgresql+asyncpg://...")
await sw.init_database()

app.add_middleware(
    ShadowWatchMiddleware,
    shadowwatch=sw,
    extract_user_id=lambda request: request.state.user_id,
    extract_entity_id=lambda request: request.path_params.get("symbol"),
    extract_action=lambda request: request.method.lower()
)

@app.get("/stocks/{symbol}")
async def get_stock(symbol: str):
    # Shadow Watch auto-tracks this request
    return {"symbol": symbol, "price": 185.20}
```

---

## Production Deployment

### Multi-Instance (Redis required)

When running multiple workers (Gunicorn, Kubernetes), add Redis so fingerprints are shared across instances:

```python
sw = ShadowWatch(
    database_url="postgresql+asyncpg://...",
    redis_url="redis://localhost:6379"  # Shared cache
)
```

### Single Instance (No Redis needed)

```python
sw = ShadowWatch(
    database_url="postgresql+asyncpg://...",
    # No redis_url → in-memory cache, fine for single process
)
```

---

## Action Weights

| Action      | Weight | Meaning                    |
| ----------- | ------ | -------------------------- |
| `view`      | 1      | Lowest intent              |
| `search`    | 3      | Active interest            |
| `alert`     | 5      | High interest              |
| `watchlist` | 8      | Strong intent              |
| `trade`     | 10     | Highest intent — auto-pins |

---

## Library Management

```python
await sw.pin_item(user_id=123, entity_id="AAPL")    # Prevent pruning
await sw.unpin_item(user_id=123, entity_id="AAPL")  # Allow pruning
await sw.remove_item(user_id=123, entity_id="MSFT") # Manual removal
library = await sw.get_library(user_id=123)         # Get sorted list
```

---

## GDPR Compliance

```python
# Export all user data
data = await sw.export_user_data(user_id=123)

# Delete everything for a user (right to be forgotten)
await sw.delete_user(user_id=123)

# Prune old activity logs
await sw.prune_old_activities(days=90)
```

---

## Security Best Practices

```python
# ✅ Always read credentials from environment variables
import os
sw = ShadowWatch(database_url=os.getenv("DATABASE_URL"))

# ✅ Always get user_id from authenticated session — never from user input
user_id = request.state.user.id  # From your auth middleware

# ✅ Wrap tracking in try/except — never let Shadow Watch crash your app
try:
    await sw.track(user_id=user_id, entity_id="AAPL", action="view")
except Exception as e:
    logger.error(f"Tracking failed: {e}")
```

---

## Troubleshooting

**`No module named 'shadowwatch'`**

```bash
pip install shadowwatch
```

**`Redis connection refused`**
Remove `redis_url` to use in-memory cache, or start Redis:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**`asyncpg.exceptions.UndefinedTableError`**
You haven't called `await sw.init_database()` yet.

---

## Examples

See [`/examples`](../examples/) for:

- `fastapi_example.py` — Full FastAPI integration
- `standalone_usage.py` — Direct Python usage
- `ecommerce_example.py`, `gaming_example.py`, `social_media_example.py` — Industry patterns

---

## Next Steps

1. ✅ Install Shadow Watch
2. ✅ Initialize with your database URL
3. ✅ Call `init_database()`
4. ✅ Add `track()` calls in your app
5. ✅ Use `verify_login()` for ATO protection
6. ✅ Deploy to production with PostgreSQL + optional Redis

**Welcome to Shadow Watch!** 🌑
