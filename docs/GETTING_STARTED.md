# Shadow Watch - Getting Started Guide

## Installation

### Basic Installation

```bash
pip install shadowwatch
```

### With Optional Dependencies

```bash
# With Redis support (recommended for production)
pip install shadowwatch[redis]

# With FastAPI integration
pip install shadowwatch[fastapi]

# Everything
pip install shadowwatch[redis,fastapi]
```

---

## Quick Start (5 Minutes)

### 1. Get a Trial License Key

Get a free 30-day trial license at: https://shadow-watch-three.vercel.app/

Or email: tanishqdasari2004@gmail.com

---

### 2. Set Up Database

Shadow Watch requires a PostgreSQL or SQLite database.

**For development (SQLite):**

```python
database_url = "sqlite+aiosqlite:///./shadowwatch.db"
```

**For production (PostgreSQL):**

```python
database_url = "postgresql+asyncpg://user:password@localhost:5432/mydb"
```

---

### 3. Initialize Shadow Watch

```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="sqlite+aiosqlite:///./shadowwatch.db",
    license_key="SW-TRIAL-XXXX-XXXX-XXXX-XXXX"
)
```

---

### 4. Create Database Tables

```python
from shadowwatch.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(database_url)

async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

---

### 5. Track User Activity

```python
# Track a user viewing an asset
await sw.track(
    user_id=123,
    entity_id="AAPL",
    action="view",
    metadata={"source": "watchlist"}
)

# Track a search
await sw.track(
    user_id=123,
    entity_id="TECH_STOCKS",
    action="search",
    metadata={"query": "tech stocks"}
)

# Track a trade (highest weight)
await sw.track(
    user_id=123,
    entity_id="AAPL",
    action="trade",
    metadata={"quantity": 10, "price": 185.20}
)
```

---

### 6. Get User Profile

```python
# Get user's behavioral profile
profile = await sw.get_profile(user_id=123)

print(profile)
# Output:
# {
#   "total_items": 15,
#   "fingerprint": "a7f9e2c4b8d1...",
#   "library": [
#     {"entity_id": "AAPL", "score": 0.85, "is_pinned": True},
#     {"entity_id": "MSFT", "score": 0.72, "is_pinned": False},
#     ...
#   ]
# }
```

---

### 7. Verify Login (Behavioral Biometric)

```python
# Verify if login is legitimate based on behavioral fingerprint
trust = await sw.verify_login(
    user_id=123,
    request_context={
        "ip": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "device_fingerprint": "abc123...",
        "library_fingerprint": "a7f9e2c4b8d1..."  # From user's cache
    }
)

print(trust)
# Output:
# {
#   "trust_score": 0.85,  # 0.0-1.0
#   "risk_level": "low",   # low/medium/high
#   "action": "allow"      # allow/require_mfa/block
# }

# Handle based on trust score
if trust["action"] == "allow":
    # Proceed with login
    pass
elif trust["action"] == "require_mfa":
    # Request additional authentication
    pass
else:  # block
    # Deny login attempt
    pass
```

---

## FastAPI Integration (Automatic Tracking)

### Basic Setup

```python
from fastapi import FastAPI
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware

app = FastAPI()

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url="postgresql+asyncpg://...",
    license_key="SW-TRIAL-XXXX-XXXX-XXXX-XXXX"
)

# Add middleware for automatic tracking
app.add_middleware(
    ShadowWatchMiddleware,
    shadowwatch=sw,
    extract_user_id=lambda request: request.state.user_id,  # Your auth logic
    extract_entity_id=lambda request: request.path_params.get("symbol"),
    extract_action=lambda request: request.method.lower()
)

@app.get("/stocks/{symbol}")
async def get_stock(symbol: str):
    # Shadow Watch automatically tracks this as:
    # user_id=request.state.user_id
    # entity_id=symbol
    # action="get"
    return {"symbol": symbol, "price": 185.20}
```

---

## Production Deployment

### Multi-Instance Setup (Redis Required)

When deploying with multiple workers (Gunicorn, Kubernetes), use Redis for shared cache:

```python
sw = ShadowWatch(
    database_url="postgresql+asyncpg://...",
    license_key="SW-...",
    redis_url="redis://localhost:6379"  # REQUIRED for multi-instance!
)
```

**Why Redis is needed:**
- License verification cached across all instances
- Fingerprints shared between workers
- No stale data issues

---

### Single-Instance Setup (No Redis)

For development or single-process deployments:

```python
sw = ShadowWatch(
    database_url="sqlite+aiosqlite:///./shadowwatch.db",
    license_key="SW-..."
    # No redis_url → uses in-memory cache (fine for single instance)
)
```

---

## Action Weights

Shadow Watch assigns different weights to different actions:

| Action | Weight | Use Case |
|--------|--------|----------|
| `view` | 1 | Viewing a stock page |
| `search` | 3 | Searching for assets |
| `alert` | 5 | Setting price alerts |
| `watchlist` | 8 | Adding to watchlist |
| `trade` | 10 | Executing trades (HIGHEST) |

**Why trades are weighted highest:**
- Real money invested = highest intent signal
- Automatic pinning (immune to pruning)
- Strongest behavioral indicator

---

## Library Management

### Automatic Pruning

When user's library exceeds 50 items:
- Lowest-scored, unpinned, oldest item is removed
- User receives email notification
- 48-hour undo window

### Manual Operations

```python
# Pin an important item (prevent pruning)
await sw.pin_item(user_id=123, entity_id="AAPL")

# Unpin
await sw.unpin_item(user_id=123, entity_id="AAPL")

# Remove manually
await sw.remove_item(user_id=123, entity_id="MSFT")

# Get library
library = await sw.get_library(user_id=123)
```

---

## Security Best Practices

### 1. Store License Key Securely

```python
# ❌ DON'T: Hardcode in source
sw = ShadowWatch(license_key="SW-TRIAL-1234-5678-9012-3456")

# ✅ DO: Use environment variables
import os
sw = ShadowWatch(license_key=os.getenv("SHADOWWATCH_LICENSE_KEY"))
```

---

### 2. Use HTTPS for License Server

License verification calls `https://shadow-watch-three.vercel.app/verify`

Ensure your production environment allows HTTPS outbound.

---

### 3. Validate User IDs

```python
# ❌ DON'T: Trust user input directly
user_id = request.query_params.get("user_id")
await sw.track(user_id=user_id, ...)

# ✅ DO: Use authenticated user from session
user_id = request.state.user.id  # From your auth middleware
await sw.track(user_id=user_id, ...)
```

---

## Troubleshooting

### "License key invalid or expired"

**Cause:** Trial expired or invalid key

**Solution:** 
1. Check expiration date: https://shadow-watch-three.vercel.app/verify
2. Email tanishqdasari2004@gmail.com for new trial

---

### "Cannot connect to license server"

**Cause:** Network/firewall blocking HTTPS to Vercel

**Solution:**
1. Check internet connection
2. Verify firewall allows `https://shadow-watch-three.vercel.app`
3. Check proxy settings

---

### "Redis connection failed"

**Cause:** Redis not available but `redis_url` provided

**Solution:**
1. For development: Remove `redis_url` (uses in-memory cache)
2. For production: Ensure Redis is running
3. Verify connection string: `redis://host:port`

---

## Examples

See `/examples` directory for:
- `fastapi_example.py` - Complete FastAPI integration
- `standalone_usage.py` - Direct API usage without framework

---

## Need Help?

- **GitHub Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com
- **Documentation:** https://github.com/Tanishq1030/Shadow_Watch#readme

---

## Next Steps

1. ✅ Install Shadow Watch
2. ✅ Get trial license
3. ✅ Follow Quick Start
4. ✅ Integrate into your app
5. ✅ Deploy to production
6. ✅ Upgrade to paid license when ready

**Welcome to Shadow Watch!** 🌑
