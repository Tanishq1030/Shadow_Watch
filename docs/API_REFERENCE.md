# Shadow Watch - API Reference

Complete reference for all Shadow Watch classes, methods, and configurations.

---

## Table of Contents

- [ShadowWatch Class](#shadowwatch-class)
- [Tracking Methods](#tracking-methods)
- [Profile Methods](#profile-methods)
- [Login Verification](#login-verification)
- [Library Management](#library-management)
- [Models](#models)
- [Integrations](#integrations)
- [Utilities](#utilities)

---

## ShadowWatch Class

Main class for interacting with Shadow Watch.

### Constructor

```python
ShadowWatch(
    database_url: str,
    license_key: str,
    redis_url: Optional[str] = None
)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `database_url` | `str` | Yes | SQLAlchemy connection string |
| `license_key` | `str` | Yes | Shadow Watch license key |
| `redis_url` | `str` | No | Redis URL (required for multi-instance deployments) |

**Supported database URLs:**

```python
# SQLite (development)
"sqlite+aiosqlite:///./shadowwatch.db"

# PostgreSQL (production)
"postgresql+asyncpg://user:pass@host:port/dbname"

# MySQL (if needed)
"mysql+aiomysql://user:pass@host:port/dbname"
```

**Examples:**

```python
# Development (single instance, no Redis)
sw = ShadowWatch(
    database_url="sqlite+aiosqlite:///./shadowwatch.db",
    license_key="SW-TRIAL-XXXX-XXXX-XXXX-XXXX"
)

# Production (multi-instance, with Redis)
sw = ShadowWatch(
    database_url="postgresql+asyncpg://user:pass@localhost/mydb",
    license_key="SW-PROD-XXXX-XXXX-XXXX-XXXX",
    redis_url="redis://localhost:6379"
)
```

---

## Tracking Methods

### `track()`

Track user activity silently.

```python
await sw.track(
    user_id: int,
    entity_id: str,
    action: str,
    metadata: Optional[Dict] = None
)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `int` | Yes | Unique user identifier |
| `entity_id` | `str` | Yes | Asset/entity identifier (e.g., "AAPL", "BTC") |
| `action` | `str` | Yes | Action type (see Action Types below) |
| `metadata` | `Dict` | No | Additional context (stored as JSON) |

**Action Types & Weights:**

| Action | Weight | Use Case |
|--------|--------|----------|
| `view` | 1 | User views asset page |
| `search` | 3 | User searches for asset |
| `alert` | 5 | User sets price alert |
| `watchlist` | 8 | User adds to watchlist |
| `trade` | 10 | User executes trade (highest intent) |

**Examples:**

```python
# Track view
await sw.track(
    user_id=123,
    entity_id="AAPL",
    action="view",
    metadata={"source": "homepage"}
)

# Track search
await sw.track(
    user_id=123,
    entity_id="TECH_STOCKS",
    action="search",
    metadata={"query": "tech stocks", "results_count": 25}
)

# Track trade (auto-pins entity)
await sw.track(
    user_id=123,
    entity_id="AAPL",
    action="trade",
    metadata={
        "side": "buy",
        "quantity": 10,
        "price": 185.20,
        "total": 1852.00
    }
)
```

**Returns:** `None`

**Raises:**
- `ValueError`: Invalid action type
- `LicenseError`: Invalid or expired license

---

## Profile Methods

### `get_profile()`

Get user's complete behavioral profile.

```python
await sw.get_profile(user_id: int) -> Dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `int` | Yes | User identifier |

**Returns:**

```python
{
    "total_items": int,           # Number of items in library
    "fingerprint": str,            # Behavioral fingerprint hash
    "library": [                   # Top interests
        {
            "entity_id": str,
            "score": float,        # 0.0-1.0
            "is_pinned": bool,
            "activity_count": int,
            "last_interaction": str  # ISO timestamp
        },
        ...
    ]
}
```

**Example:**

```python
profile = await sw.get_profile(user_id=123)

print(f"User has {profile['total_items']} interests")
print(f"Fingerprint: {profile['fingerprint'][:16]}...")

for item in profile['library'][:5]:  # Top 5
    print(f"  {item['entity_id']}: {item['score']:.2f}")
```

---

### `get_fingerprint()`

Get just the behavioral fingerprint.

```python
await sw.get_fingerprint(user_id: int) -> str
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `int` | Yes | User identifier |

**Returns:** `str` - SHA256 hash of user's behavioral pattern

**Example:**

```python
fingerprint = await sw.get_fingerprint(user_id=123)
# Returns: "a7f9e2c4b8d1f3a2c5e7d9f1b3a5c7e9..."
```

---

## Login Verification

### `verify_login()`

Calculate trust score for login attempt based on behavioral fingerprint.

```python
await sw.verify_login(
    user_id: int,
    request_context: Dict
) -> Dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | `int` | Yes | User attempting login |
| `request_context` | `Dict` | Yes | Request metadata (see below) |

**Request Context Structure:**

```python
request_context = {
    "ip": str,                      # IP address
    "user_agent": str,              # Browser user agent
    "device_fingerprint": str,      # Device fingerprint (optional)
    "library_fingerprint": str      # Stored fingerprint from user's cache
}
```

**Returns:**

```python
{
    "trust_score": float,          # 0.0-1.0 (higher = more trustworthy)
    "risk_level": str,             # "low" | "medium" | "high"
    "action": str,                 # "allow" | "require_mfa" | "block"
    "factors": {
        "fingerprint_match": float,  # 0.0-1.0
        "ip_familiarity": float,
        "device_familiarity": float,
        "time_pattern": float
    }
}
```

**Trust Score Thresholds:**

| Score Range | Risk Level | Recommended Action |
|-------------|------------|-------------------|
| 0.80 - 1.00 | Low | Allow login |
| 0.60 - 0.79 | Medium | Require MFA |
| 0.00 - 0.59 | High | Block + notify user |

**Example:**

```python
# During login attempt
trust = await sw.verify_login(
    user_id=123,
    request_context={
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "device_fingerprint": request.cookies.get("device_fp"),
        "library_fingerprint": request.json.get("fingerprint")
    }
)

# Handle based on action
if trust["action"] == "allow":
    # Proceed with login
    return {"success": True, "token": generate_token()}

elif trust["action"] == "require_mfa":
    # Request 2FA
    return {"success": False, "require_mfa": True}

else:  # "block"
    # Deny + alert user
    send_security_alert(user_id=123)
    return {"success": False, "error": "Suspicious login attempt"}
```

---

## Library Management

### `pin_item()`

Pin an item to prevent pruning.

```python
await sw.pin_item(user_id: int, entity_id: str)
```

**Example:**

```python
# User manually pins AAPL
await sw.pin_item(user_id=123, entity_id="AAPL")
```

---

### `unpin_item()`

Unpin an item (allows pruning).

```python
await sw.unpin_item(user_id: int, entity_id: str)
```

---

### `remove_item()`

Manually remove item from library.

```python
await sw.remove_item(user_id: int, entity_id: str)
```

---

### `get_library()`

Get user's complete library.

```python
await sw.get_library(user_id: int, limit: int = 50) -> List[Dict]
```

**Returns:**

```python
[
    {
        "entity_id": "AAPL",
        "score": 0.85,
        "is_pinned": True,
        "activity_count": 42,
        "first_seen": "2026-01-01T00:00:00Z",
        "last_interaction": "2026-01-10T15:30:00Z"
    },
    ...
]
```

---

## Models

### UserActivityEvent

Raw activity events.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key |
| `user_id` | `int` | User identifier |
| `entity_id` | `str` | Asset identifier |
| `action` | `str` | Action type |
| `metadata` | `JSON` | Additional context |
| `created_at` | `datetime` | Timestamp |

---

### UserInterest

Aggregated interest scores.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key |
| `user_id` | `int` | User identifier |
| `entity_id` | `str` | Asset identifier |
| `score` | `float` | Interest score (0.0-1.0) |
| `activity_count` | `int` | Total interactions |
| `is_pinned` | `bool` | Protected from pruning |
| `first_seen` | `datetime` | First interaction |
| `last_interaction` | `datetime` | Most recent interaction |

---

### LibraryVersion

Behavioral fingerprint snapshots.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key |
| `user_id` | `int` | User identifier |
| `version` | `int` | Snapshot version number |
| `fingerprint` | `str` | SHA256 hash |
| `snapshot_data` | `JSON` | Complete library state |
| `created_at` | `datetime` | Snapshot timestamp |

---

## Integrations

### FastAPI Middleware

Automatic activity tracking for FastAPI applications.

```python
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware

app.add_middleware(
    ShadowWatchMiddleware,
    shadowwatch=sw,
    extract_user_id=lambda request: request.state.user_id,
    extract_entity_id=lambda request: request.path_params.get("symbol"),
    extract_action=lambda request: request.method.lower()
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `shadowwatch` | `ShadowWatch` | Shadow Watch instance |
| `extract_user_id` | `Callable` | Function to extract user ID from request |
| `extract_entity_id` | `Callable` | Function to extract entity ID from request |
| `extract_action` | `Callable` | Function to extract action from request |

**Example:**

```python
@app.get("/stocks/{symbol}")
async def get_stock(symbol: str, request: Request):
    # Middleware automatically calls:
    # await sw.track(
    #     user_id=request.state.user_id,
    #     entity_id=symbol,
    #     action="get"
    # )
    
    return {"symbol": symbol, "price": 185.20}
```

---

## Utilities

### License Verification

```python
from shadowwatch.utils.license import verify_license

# Manually verify license
result = await verify_license("SW-TRIAL-XXXX-XXXX-XXXX-XXXX")

# Returns:
# {
#     "valid": True,
#     "tier": "trial",
#     "max_events": 10000,
#     "expires_at": "2026-02-09T..."
# }
```

---

### Input Validation

```python
from shadowwatch.utils.validators import validate_action

# Validate action type
is_valid = validate_action("trade")  # True
is_valid = validate_action("invalid")  # False
```

---

## Configuration

### Environment Variables

Shadow Watch reads these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SHADOWWATCH_LICENSE_KEY` | License key | (required) |
| `SHADOWWATCH_DATABASE_URL` | Database connection | (required) |
| `SHADOWWATCH_REDIS_URL` | Redis connection | `None` |
| `SHADOWWATCH_LOG_LEVEL` | Logging level | `INFO` |

**Example `.env` file:**

```bash
SHADOWWATCH_LICENSE_KEY=SW-TRIAL-XXXX-XXXX-XXXX-XXXX
SHADOWWATCH_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
SHADOWWATCH_REDIS_URL=redis://localhost:6379
SHADOWWATCH_LOG_LEVEL=DEBUG
```

---

## Error Handling

### Common Exceptions

**LicenseError:**
```python
try:
    sw = ShadowWatch(database_url="...", license_key="INVALID")
except LicenseError as e:
    print(f"License error: {e}")
    # "License key invalid or expired"
```

**ValidationError:**
```python
try:
    await sw.track(user_id=123, entity_id="AAPL", action="invalid_action")
except ValidationError as e:
    print(f"Validation error: {e}")
    # "Invalid action type: invalid_action"
```

**DatabaseError:**
```python
try:
    await sw.track(user_id=123, entity_id="AAPL", action="view")
except DatabaseError as e:
    print(f"Database error: {e}")
    # "Failed to insert activity event"
```

---

## Best Practices

### 1. Always Use Environment Variables

```python
# ❌ DON'T
sw = ShadowWatch(license_key="SW-TRIAL-...")

# ✅ DO
import os
sw = ShadowWatch(license_key=os.getenv("SHADOWWATCH_LICENSE_KEY"))
```

---

### 2. Use Redis in Production

```python
# ❌ DON'T (multi-instance without Redis)
sw = ShadowWatch(database_url="...", license_key="...")

# ✅ DO (multi-instance with Redis)
sw = ShadowWatch(
    database_url="...",
    license_key="...",
    redis_url="redis://localhost:6379"
)
```

---

### 3. Validate User IDs

```python
# ❌ DON'T (trust user input)
user_id = request.query_params.get("user_id")
await sw.track(user_id=user_id, ...)

# ✅ DO (use authenticated session)
user_id = request.state.user.id  # From auth middleware
await sw.track(user_id=user_id, ...)
```

---

### 4. Handle Errors Gracefully

```python
# ❌ DON'T (let Shadow Watch crash your app)
await sw.track(user_id=123, entity_id="AAPL", action="view")

# ✅ DO (catch exceptions)
try:
    await sw.track(user_id=123, entity_id="AAPL", action="view")
except Exception as e:
    logger.error(f"Shadow Watch error: {e}")
    # App continues working even if Shadow Watch fails
```

---

## Performance Considerations

### Caching

- License verification: Cached 24 hours
- Fingerprints: Cached 24 hours (Redis) or per-request (memory)
- Profiles: Not cached (always fresh)

### Database Queries

- `track()`: 2 queries (insert + update)
- `get_profile()`: 3 queries (select user interests + calculate fingerprint + get library)
- `verify_login()`: 1 query (get stored fingerprint)

### Recommended Indexes

```sql
-- For fast user lookups
CREATE INDEX idx_activity_user_id ON shadow_watch_activity_events(user_id);
CREATE INDEX idx_interests_user_id ON shadow_watch_interests(user_id);

-- For timestamp queries
CREATE INDEX idx_activity_created_at ON shadow_watch_activity_events(created_at);

-- For entity lookups
CREATE INDEX idx_interests_entity ON shadow_watch_interests(entity_id);
```

---

## Support

- **Documentation:** https://github.com/Tanishq1030/Shadow_Watch#readme
- **Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com
- **License Server:** https://shadow-watch-three.vercel.app

---

**Last Updated:** January 11, 2026  
**Version:** 0.1.0
