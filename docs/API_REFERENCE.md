# Shadow Watch — Full API Reference

Complete reference for all `ShadowWatch` methods, models, integrations, and configuration.

---

## Table of Contents

- [ShadowWatch Class](#shadowwatch-class)
- [Tracking Methods](#tracking-methods)
- [Profile Methods](#profile-methods)
- [Login Verification](#login-verification)
- [Continuity (ATO Detection)](#continuity-ato-detection)
- [Library Management](#library-management)
- [GDPR Methods](#gdpr-methods)
- [Database Models](#database-models)
- [Integrations](#integrations)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Performance](#performance)

---

## ShadowWatch Class

### Constructor

```python
ShadowWatch(
    database_url: str,
    redis_url: Optional[str] = None
)
```

**Parameters:**

| Parameter      | Type  | Required | Description                                        |
| -------------- | ----- | -------- | -------------------------------------------------- |
| `database_url` | `str` | ✅       | SQLAlchemy async connection string                 |
| `redis_url`    | `str` | ❌       | Redis URL for distributed caching (multi-instance) |

**Supported database URLs:**

```python
# PostgreSQL (recommended for production)
"postgresql+asyncpg://user:pass@host:5432/dbname"

# MySQL
"mysql+aiomysql://user:pass@host:3306/dbname"

# SQLite (local development only)
"sqlite+aiosqlite:///./dev.db"
```

**Examples:**

```python
# Local development
sw = ShadowWatch(
    database_url="sqlite+aiosqlite:///./dev.db"
)

# Production — single instance
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL")
)

# Production — multi-instance with Redis
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    redis_url=os.getenv("REDIS_URL")
)
```

### `init_database()`

Create all required tables. Call once on startup.

```python
await sw.init_database()
```

---

## Tracking Methods

### `track()`

Silently log user activity.

```python
await sw.track(
    user_id: int,
    entity_id: str,
    action: str,
    metadata: Optional[Dict] = None
) -> None
```

**Parameters:**

| Parameter   | Type   | Required | Description                                    |
| ----------- | ------ | -------- | ---------------------------------------------- |
| `user_id`   | `int`  | ✅       | Unique user identifier                         |
| `entity_id` | `str`  | ✅       | Asset/entity (e.g., `"AAPL"`, `"product_123"`) |
| `action`    | `str`  | ✅       | Action type (see weights below)                |
| `metadata`  | `dict` | ❌       | Arbitrary JSON context                         |

**Action weights:**

| Action      | Weight | Use Case                                |
| ----------- | ------ | --------------------------------------- |
| `view`      | 1      | Page view                               |
| `search`    | 3      | Search query                            |
| `alert`     | 5      | Price/notification alert set            |
| `watchlist` | 8      | Added to watchlist                      |
| `trade`     | 10     | Transaction executed (auto-pins entity) |

**Examples:**

```python
# Simple view
await sw.track(user_id=123, entity_id="AAPL", action="view")

# Search with metadata
await sw.track(
    user_id=123,
    entity_id="TECH_STOCKS",
    action="search",
    metadata={"query": "tech stocks", "results": 42}
)

# Trade (auto-pins + highest weight)
await sw.track(
    user_id=123,
    entity_id="AAPL",
    action="trade",
    metadata={"side": "buy", "quantity": 10, "price": 185.20}
)
```

---

## Profile Methods

### `get_profile()`

Get a user's complete behavioral profile.

```python
profile = await sw.get_profile(user_id: int) -> Dict
```

**Returns:**

```python
{
    "user_id": 123,
    "total_items": 15,
    "fingerprint": "a7f9e2c4b8d1f3a2...",  # SHA256 behavioral hash
    "entropy": 0.73,                           # Diversity score 0-1
    "library": [
        {
            "entity_id": "AAPL",
            "score": 0.85,
            "is_pinned": True,
            "activity_count": 42,
            "first_seen": "2026-01-01T00:00:00Z",
            "last_interaction": "2026-01-20T15:30:00Z"
        },
        ...
    ]
}
```

### `get_fingerprint()`

Get just the behavioral fingerprint hash.

```python
fingerprint = await sw.get_fingerprint(user_id: int) -> str
# → "a7f9e2c4b8d1f3a2c5e7d9f1b3a5c7e9..."
```

---

## Login Verification

### `verify_login()`

Calculate a behavioral trust score for a login attempt.

```python
trust = await sw.verify_login(
    user_id: int,
    request_context: Dict
) -> Dict
```

**Request context:**

```python
request_context = {
    "ip": str,                  # Client IP address
    "user_agent": str,          # Browser user agent
    "device_fingerprint": str,  # Optional device fingerprint
    "library_fingerprint": str  # Stored fingerprint from client cache
}
```

**Returns:**

```python
{
    "trust_score": 0.87,     # 0.0–1.0 (higher = safer)
    "risk_level": "low",     # "low" | "medium" | "high"
    "action": "allow",       # "allow" | "require_mfa" | "block"
    "factors": {
        "fingerprint_match": 0.92,
        "ip_familiarity": 0.85,
        "device_familiarity": 0.78,
        "time_pattern": 0.90
    }
}
```

**Trust thresholds:**

| Score       | Risk   | Recommended Action  |
| ----------- | ------ | ------------------- |
| 0.80 – 1.00 | Low    | Allow login         |
| 0.60 – 0.79 | Medium | Require MFA         |
| 0.00 – 0.59 | High   | Block + notify user |

**Example:**

```python
@app.post("/auth/login")
async def login(credentials: LoginCredentials, request: Request):
    user = await authenticate(credentials)

    trust = await sw.verify_login(
        user_id=user.id,
        request_context={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "device_fingerprint": request.cookies.get("device_fp"),
        }
    )

    if trust["action"] == "allow":
        return {"token": generate_jwt(user.id)}
    elif trust["action"] == "require_mfa":
        send_mfa_code(user.id)
        return {"require_mfa": True}
    else:
        send_security_alert(user.id)
        raise HTTPException(403, "Suspicious login detected")
```

---

## Continuity (ATO Detection)

### `calculate_continuity()`

Measure whether the current actor is still the original account owner. Core ATO (Account Takeover) detection method.

```python
result = await sw.calculate_continuity(subject_id: str) -> Dict
```

**Returns:**

```python
{
    "score": 0.82,      # 0.0–1.0 (higher = more continuous/stable)
    "state": "stable",  # "stable" | "drifting" | "anomalous"
    "confidence": 0.91  # Statistical confidence of the score
}
```

**Score interpretation:**

| Score     | State       | Meaning                                  |
| --------- | ----------- | ---------------------------------------- |
| ≥ 0.75    | `stable`    | Same actor — high confidence             |
| 0.50–0.74 | `drifting`  | Possible session hijack — monitor        |
| < 0.50    | `anomalous` | Likely account takeover — trigger review |

---

## Library Management

### `pin_item()` / `unpin_item()`

```python
await sw.pin_item(user_id: int, entity_id: str)    # Mark as permanent
await sw.unpin_item(user_id: int, entity_id: str)  # Allow pruning
```

### `remove_item()`

```python
await sw.remove_item(user_id: int, entity_id: str)  # Remove from library
```

### `get_library()`

```python
library = await sw.get_library(user_id: int, limit: int = 50) -> List[Dict]
```

**Returns:**

```python
[
    {
        "entity_id": "AAPL",
        "score": 0.95,
        "is_pinned": True,
        "activity_count": 42,
        "first_seen": "2026-01-01T00:00:00Z",
        "last_interaction": "2026-01-20T15:30:00Z"
    },
    ...
]
```

---

## GDPR Methods

### `export_user_data()`

Export all data for a user (data portability).

```python
data = await sw.export_user_data(user_id: int) -> Dict
```

### `delete_user()`

Delete all user data (right to be forgotten).

```python
await sw.delete_user(user_id: int)
```

Deletes from: `activity_events`, `interests`, `library_versions`.

### `prune_old_activities()`

Delete activity logs older than N days.

```python
deleted_count = await sw.prune_old_activities(days: int = 90) -> int
```

---

## Database Models

### `UserActivityEvent`

Raw activity log.

| Field        | Type       | Description        |
| ------------ | ---------- | ------------------ |
| `id`         | `int`      | Primary key        |
| `user_id`    | `int`      | User identifier    |
| `entity_id`  | `str`      | Asset/entity       |
| `action`     | `str`      | Action type        |
| `metadata`   | `JSON`     | Additional context |
| `created_at` | `datetime` | Timestamp          |

### `UserInterest`

Aggregated interest scores.

| Field              | Type       | Description              |
| ------------------ | ---------- | ------------------------ |
| `id`               | `int`      | Primary key              |
| `user_id`          | `int`      | User identifier          |
| `entity_id`        | `str`      | Asset/entity             |
| `score`            | `float`    | Interest score (0.0–1.0) |
| `activity_count`   | `int`      | Total interactions       |
| `is_pinned`        | `bool`     | Protected from pruning   |
| `first_seen`       | `datetime` | First interaction        |
| `last_interaction` | `datetime` | Most recent              |

### `LibraryVersion`

Behavioral fingerprint snapshots for continuity tracking.

| Field           | Type       | Description        |
| --------------- | ---------- | ------------------ |
| `id`            | `int`      | Primary key        |
| `user_id`       | `int`      | User identifier    |
| `version`       | `int`      | Snapshot number    |
| `fingerprint`   | `str`      | SHA256 hash        |
| `snapshot_data` | `JSON`     | Full library state |
| `created_at`    | `datetime` | Snapshot timestamp |

---

## Integrations

### FastAPI Middleware

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

| Parameter           | Type          | Description                 |
| ------------------- | ------------- | --------------------------- |
| `shadowwatch`       | `ShadowWatch` | Initialized instance        |
| `extract_user_id`   | `Callable`    | Gets user ID from request   |
| `extract_entity_id` | `Callable`    | Gets entity ID from request |
| `extract_action`    | `Callable`    | Gets action from request    |

---

## Configuration

### Environment Variables

| Variable                | Description                                | Required |
| ----------------------- | ------------------------------------------ | -------- |
| `DATABASE_URL`          | SQLAlchemy async connection string         | ✅       |
| `REDIS_URL`             | Redis for distributed cache                | ❌       |
| `SHADOWWATCH_LOG_LEVEL` | Logging level (`INFO`, `DEBUG`, `WARNING`) | ❌       |

**.env example:**

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb
REDIS_URL=redis://localhost:6379
SHADOWWATCH_LOG_LEVEL=INFO
```

### Recommended Database Indexes

```sql
CREATE INDEX idx_activity_user_id ON shadow_watch_activity_events(user_id);
CREATE INDEX idx_activity_created_at ON shadow_watch_activity_events(created_at);
CREATE INDEX idx_interests_user_id ON shadow_watch_interests(user_id);
CREATE INDEX idx_interests_score ON shadow_watch_interests(score DESC);
CREATE INDEX idx_interests_entity ON shadow_watch_interests(entity_id);
```

---

## Error Handling

```python
try:
    await sw.track(user_id=123, entity_id="AAPL", action="view")
except ValueError as e:
    # Invalid action type, missing required field, etc.
    logger.warning(f"Tracking validation error: {e}")
except Exception as e:
    # Database error, connection issue, etc.
    logger.error(f"Shadow Watch error: {e}")
    # Always let your app continue — tracking should never crash your service
```

---

## Best Practices

### 1. Use Environment Variables

```python
# ✅ DO
sw = ShadowWatch(database_url=os.getenv("DATABASE_URL"))

# ❌ DON'T hardcode credentials
sw = ShadowWatch(database_url="postgresql://root:password@prod-db/live")
```

### 2. Use Redis in Production (Multi-Instance)

```python
# ✅ For Kubernetes / Gunicorn multi-worker setups
sw = ShadowWatch(
    database_url=os.getenv("DATABASE_URL"),
    redis_url=os.getenv("REDIS_URL")
)
```

### 3. Always Use Authenticated User IDs

```python
# ✅ From auth middleware
user_id = request.state.user.id

# ❌ Never trust user-provided IDs
user_id = request.query_params.get("user_id")
```

### 4. Wrap Tracking in Try/Except

```python
# ✅ Tracking failure must never crash your app
try:
    await sw.track(...)
except Exception as e:
    logger.error(f"Tracking failed: {e}")
```

---

## Performance

### Benchmarks

| Method                   | With Redis | DB Only |
| ------------------------ | ---------- | ------- |
| `track()`                | ~10ms      | ~15ms   |
| `get_profile()`          | ~5ms       | ~20ms   |
| `get_library()`          | ~5ms       | ~15ms   |
| `verify_login()`         | ~15ms      | ~25ms   |
| `calculate_continuity()` | ~20ms      | ~35ms   |
| `pin_item()`             | ~3ms       | ~8ms    |

_Benchmarked on PostgreSQL 14, Redis 7, 1,000 concurrent users._

### Caching Strategy

- **Fingerprints:** Cached 24 hours in Redis (or in-memory for single instance)
- **Profiles:** Always fetched fresh from DB
- **Interests:** Cached per-session in Redis

---

## Support

- **GitHub:** https://github.com/Tanishq1030/Shadow_Watch
- **Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com

---

**Version:** 2.0.0 — Free and open source (MIT)
