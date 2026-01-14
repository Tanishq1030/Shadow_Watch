# Shadow Watch API Reference

## Core Methods

Shadow Watch is a **Python package**, not a REST API. You use it directly in your Python code.

---

## 📦 Installation

```bash
pip install shadowwatch
```

---

## 🔧 Initialization

```python
from shadowwatch import ShadowWatch
import asyncio

async def main():
    sw = ShadowWatch(
        database_url="sqlite+aiosqlite:///./shadowwatch.db",  # or PostgreSQL, MySQL
        license_key="SW-TRIAL-YOUR-KEY-HERE",
        redis_url="redis://localhost:6379"  # Optional for caching
    )
    
    await sw.init_database()  # Create tables

asyncio.run(main())
```

**Parameters:**
- `database_url` - SQLAlchemy async database URL
- `license_key` - Your Shadow Watch license key
- `redis_url` - (Optional) Redis URL for caching

---

## 📍 Core API Methods

### 1. `await sw.track(user_id, entity_id, action, metadata=None)`

**Track user activity**

```python
await sw.track(
    user_id=42,
    entity_id="AAPL",
    action="view",
    metadata={"source": "mobile"}  # Optional
)
```

**Parameters:**
- `user_id` (int/str/UUID) - User identifier
- `entity_id` (str) - What they interacted with (stock, product, article)
- `action` (str) - What they did ("view", "click", "purchase", "trade")
- `metadata` (dict, optional) - Additional context

**Returns:** `None`

**What it does:**
1. Validates input
2. Stores in `user_activities` table
3. Updates `user_profiles` (fingerprint, entropy)
4. Updates `interest_library` (view counts, scores)
5. Syncs to Redis cache (if configured)

**Time:** ~10ms

---

### 2. `await sw.get_profile(user_id)`

**Get user's behavioral profile**

```python
profile = await sw.get_profile(user_id=42)
print(profile)
```

**Returns:**
```python
{
    "user_id": 42,
    "total_items": 15,
    "fingerprint": "a3f2c1b4e5d6f7a8b9c0d1e2f3a4b5c6",
    "entropy": 0.73,
    "library": [
        {
            "entity_id": "AAPL",
            "view_count": 5,
            "last_viewed": "2026-01-13T09:00:00.123456Z",
            "score": 0.95,
            "pinned": false
        }
    ],
    "pinned_count": 0,
    "created_at": "2026-01-10T08:00:00.000000Z",
    "updated_at": "2026-01-13T09:00:00.123456Z"
}
```

**Time:** ~5ms (with Redis), ~20ms (DB only)

---

### 3. `await sw.get_library(user_id, limit=100)`

**Get user's interest library (sorted by score)**

```python
library = await sw.get_library(user_id=42, limit=10)
# Returns top 10 interests
```

**Returns:** `List[dict]` - Sorted by `score` (descending)

**Time:** ~5ms

---

### 4. `await sw.verify_login(user_id, fingerprint_data)`

**Verify login attempt and calculate trust score**

```python
trust_result = await sw.verify_login(
    user_id=42,
    fingerprint_data={
        "ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "timezone": "America/New_York"
    }
)

print(trust_result)
```

**Returns:**
```python
{
    "trust_score": 0.87,  # 0.0-1.0 (higher = more trustworthy)
    "decision": "allow",  # "allow", "mfa", "block"
    "reason": "normal_behavior",
    "fingerprint_match": true,
    "entropy_check": "passed",
    "velocity_check": "passed"
}
```

**Decision Thresholds:**
- `trust_score >= 0.8` → **allow** (login successful)
- `0.5 <= trust_score < 0.8` → **mfa** (require additional verification)
- `trust_score < 0.5` → **block** (deny login)

**Time:** ~15ms

---

### 5. `await sw.calculate_trust_score(user_id, fingerprint_data)`

**Calculate trust score without logging (for testing)**

```python
score = await sw.calculate_trust_score(
    user_id=42,
    fingerprint_data={"ip": "..."}
)
# Returns: 0.87
```

**Returns:** `float` (0.0-1.0)

---

### 6. `await sw.pin_item(user_id, entity_id)`

**Pin an item to user's library (always visible)**

```python
await sw.pin_item(user_id=42, entity_id="AAPL")
```

**Use case:** Watchlists, favorites

---

### 7. `await sw.unpin_item(user_id, entity_id)`

**Unpin an item**

```python
await sw.unpin_item(user_id=42, entity_id="AAPL")
```

---

### 8. `await sw.prune_old_activities(days=90)`

**Delete activities older than X days (GDPR compliance)**

```python
deleted_count = await sw.prune_old_activities(days=90)
print(f"Deleted {deleted_count} old activities")
```

**Returns:** `int` - Number of rows deleted

---

### 9. `await sw.export_user_data(user_id)`

**Export all user data (GDPR data export)**

```python
data = await sw.export_user_data(user_id=42)
# Returns complete JSON dump of all user data
```

**Returns:** `dict` with all user activities, profiles, library

---

### 10. `await sw.delete_user(user_id)`

**Delete all user data (GDPR right to be forgotten)**

```python
await sw.delete_user(user_id=42)
print("User 42 data deleted")
```

**Deletes:**
- All activities in `user_activities`
- Profile in `user_profiles`
- All items in `interest_library`
- All trust events in `trust_events`

---

## 🔌 FastAPI Integration

### Middleware (Automatic Tracking)

```python
from fastapi import FastAPI
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware

app = FastAPI()
sw = ShadowWatch(database_url="...", license_key="...")

app.add_middleware(
    ShadowWatchMiddleware,
    shadow_watch=sw,
    user_id_getter=lambda request: request.state.user.id,
    entity_extractor=lambda request: request.path_params.get('symbol'),
    action_mapper=lambda request: "trade" if "trade" in request.url.path else "view"
)
```

**Auto-tracks all requests** matching your rules.

---

## 📊 Database Schema

### Tables Created

1. **`user_activities`** - Raw activity events
   - `id`, `user_id`, `entity_id`, `action`, `metadata`, `created_at`

2. **`user_profiles`** - Behavioral profiles
   - `user_id`, `total_items`, `fingerprint`, `entropy`, `created_at`, `updated_at`

3. **`interest_library`** - User interests
   - `user_id`, `entity_id`, `view_count`, `last_viewed`, `score`, `pinned`

4. **`trust_events`** - Login attempts
   - `user_id`, `trust_score`, `decision`, `fingerprint_data`, `created_at`

---

## 🚀 Quick Examples

### Track Article View
```python
await sw.track(user_id=42, entity_id="python-async-guide", action="view")
```

### Track Product Purchase
```python
await sw.track(user_id=42, entity_id="product_12345", action="purchase", 
               metadata={"price": 99.99, "currency": "USD"})
```

### Check Login Trust
```python
result = await sw.verify_login(
    user_id=42,
    fingerprint_data={"ip": request.client.host, "user_agent": request.headers.get("user-agent")}
)

if result["decision"] == "block":
    raise HTTPException(status_code=403, detail="Suspicious login detected")
elif result["decision"] == "mfa":
    return {"message": "Please verify with 2FA", "trust_score": result["trust_score"]}
```

### Get User's Top Interests
```python
library = await sw.get_library(user_id=42, limit=5)
for item in library:
    print(f"{item['entity_id']}: {item['view_count']} views, score {item['score']}")
```

---

## 🔑 License Keys

Get a free 30-day trial key at: **[Your License Portal]**

Or set via environment variable:
```bash
export SHADOWWATCH_LICENSE="SW-TRIAL-YOUR-KEY-HERE"
```

---

## 🎯 Response Times (Benchmarks)

| Method | Time (with Redis) | Time (DB only) |
|--------|-------------------|----------------|
| `track()` | ~10ms | ~15ms |
| `get_profile()` | ~5ms | ~20ms |
| `get_library()` | ~5ms | ~15ms |
| `verify_login()` | ~15ms | ~25ms |
| `pin_item()` | ~3ms | ~8ms |

Tested on: PostgreSQL 14, Redis 7, 1000 concurrent users

---

## ❓ Common Patterns

### Pattern 1: E-commerce Product Tracking
```python
@app.get("/products/{product_id}")
async def view_product(product_id: str, user: User):
    await sw.track(user_id=user.id, entity_id=product_id, action="view")
    # ... rest of your logic
```

### Pattern 2: Stock Trading Platform
```python
@app.post("/trade/{symbol}")
async def execute_trade(symbol: str, user: User):
    await sw.track(user_id=user.id, entity_id=symbol, action="trade", 
                   metadata={"type": "buy", "shares": 100})
    # ... execute trade
```

### Pattern 3: Secure Login with Trust Score
```python
@app.post("/login")
async def login(credentials: LoginRequest, request: Request):
    user = authenticate(credentials)
    
    trust = await sw.verify_login(
        user_id=user.id,
        fingerprint_data={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "timezone": request.headers.get("x-timezone")
        }
    )
    
    if trust["decision"] == "block":
        raise HTTPException(403, "Account security alert. Contact support.")
    
    token = create_token(user.id)
    return {"token": token, "mfa_required": trust["decision"] == "mfa"}
```

---

**That's it!** Shadow Watch is designed to be simple. 10 methods. All async. All fast.
