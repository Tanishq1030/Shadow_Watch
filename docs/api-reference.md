# Shadow Watch — API Reference (Quick Reference)

Shadow Watch is a **Python library**, not a REST API. You call it directly in your code.

---

## Installation

```bash
pip install shadowwatch
```

---

## Initialization

```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="postgresql+asyncpg://user:pass@localhost:5432/mydb",
    redis_url="redis://localhost:6379"  # Optional — for multi-instance caching
)

await sw.init_database()  # Create tables on first run
```

**Parameters:**

| Parameter      | Type  | Required | Description                        |
| -------------- | ----- | -------- | ---------------------------------- |
| `database_url` | `str` | ✅       | SQLAlchemy async connection string |
| `redis_url`    | `str` | ❌       | Redis URL for distributed caching  |

**Supported databases:**

```python
# PostgreSQL (recommended)
"postgresql+asyncpg://user:pass@host:5432/dbname"

# MySQL
"mysql+aiomysql://user:pass@host:3306/dbname"

# SQLite (local dev only)
"sqlite+aiosqlite:///./dev.db"
```

---

## Core Methods

### `track()` — Log user activity

```python
await sw.track(
    user_id=42,
    entity_id="AAPL",
    action="view",
    metadata={"source": "mobile"}  # Optional
)
```

| Parameter   | Type             | Description                                     |
| ----------- | ---------------- | ----------------------------------------------- |
| `user_id`   | `int\|str\|UUID` | User identifier                                 |
| `entity_id` | `str`            | What they interacted with                       |
| `action`    | `str`            | `view`, `search`, `alert`, `watchlist`, `trade` |
| `metadata`  | `dict`           | Optional extra context                          |

**Action weights:** `view`=1, `search`=3, `alert`=5, `watchlist`=8, `trade`=10

---

### `get_profile()` — Get behavioral profile

```python
profile = await sw.get_profile(user_id=42)
# → {"user_id": 42, "total_items": 15, "fingerprint": "a3f2...", "library": [...]}
```

---

### `get_library()` — Get interest library

```python
library = await sw.get_library(user_id=42, limit=10)
# → [{"entity_id": "AAPL", "score": 0.95, "view_count": 5, ...}, ...]
```

---

### `verify_login()` — Trust score for logins

```python
trust = await sw.verify_login(
    user_id=42,
    fingerprint_data={
        "ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "timezone": "America/New_York"
    }
)
# → {"trust_score": 0.87, "decision": "allow", "risk_level": "low"}
```

| Score     | Decision |
| --------- | -------- |
| ≥ 0.80    | `allow`  |
| 0.60–0.79 | `mfa`    |
| < 0.60    | `block`  |

---

### `calculate_continuity()` — ATO detection

```python
continuity = await sw.calculate_continuity("user_42")
# → {"score": 0.82, "state": "stable", "confidence": 0.91}
```

---

### `pin_item()` / `unpin_item()` — Watchlist management

```python
await sw.pin_item(user_id=42, entity_id="AAPL")
await sw.unpin_item(user_id=42, entity_id="AAPL")
```

---

### `prune_old_activities()` — GDPR data retention

```python
deleted = await sw.prune_old_activities(days=90)
```

---

### `export_user_data()` / `delete_user()` — GDPR compliance

```python
data = await sw.export_user_data(user_id=42)   # → full JSON dump
await sw.delete_user(user_id=42)                # right to be forgotten
```

---

## FastAPI Middleware

```python
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware

app.add_middleware(
    ShadowWatchMiddleware,
    shadow_watch=sw,
    user_id_getter=lambda req: req.state.user.id,
    entity_extractor=lambda req: req.path_params.get("symbol"),
    action_mapper=lambda req: "trade" if "trade" in req.url.path else "view"
)
```

---

## Database Tables Created

| Table                           | Purpose                          |
| ------------------------------- | -------------------------------- |
| `shadow_watch_activity_events`  | Raw activity log                 |
| `shadow_watch_interests`        | Aggregated interest scores       |
| `shadow_watch_library_versions` | Behavioral fingerprint snapshots |

---

## Performance Benchmarks

| Method           | Redis | DB only |
| ---------------- | ----- | ------- |
| `track()`        | ~10ms | ~15ms   |
| `get_profile()`  | ~5ms  | ~20ms   |
| `verify_login()` | ~15ms | ~25ms   |
| `pin_item()`     | ~3ms  | ~8ms    |

---

## Error Handling

```python
try:
    await sw.track(user_id=123, entity_id="AAPL", action="view")
except ValueError as e:
    logger.error(f"Invalid input: {e}")
except Exception as e:
    logger.error(f"Shadow Watch error: {e}")
    # Always let your app continue even if tracking fails
```

---

## Support

- **GitHub:** https://github.com/Tanishq1030/Shadow_Watch
- **Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com
