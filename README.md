# Shadow Watch

[![PyPI version](https://badge.fury.io/py/shadowwatch.svg)](https://badge.fury.io/py/shadowwatch)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**"Like a shadow — always there, never seen."**

A passive behavioral intelligence library — fully free and open source. Tracks user activity, builds interest profiles, and detects account takeovers. No license keys. No tiers. No limits.

---

## Installation

```bash
pip install shadowwatch
```

## Quick Start

```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(database_url="postgresql+asyncpg://localhost/db")

# Track activity
await sw.track(user_id=123, entity_id="article_123", action="view")

# Get user profile
profile = await sw.get_profile(user_id=123)
# Returns: {"user_id": 123, "total_items": 10, "library": [...], "fingerprint": "abc123..."}

# ATO detection — temporal continuity
continuity = await sw.calculate_continuity("user_123")
# Returns: {"score": 0.82, "state": "stable", "confidence": 0.91}
```

---

## Features

✅ **Activity Tracking** - Silent behavioral logging  
✅ **Interest Profiles** - Auto-generated from activity  
✅ **Behavioral Fingerprints** - Stable user signatures  
✅ **Temporal Continuity** - Detect if current actor is still the account owner  
✅ **Trust Scoring** - Risk-based login verification  
✅ **No Event Limits** - Track unlimited activities  
✅ **Self-Hosted** - Your data stays on your servers  
✅ **MIT Licensed** - No keys, no tiers, no subscriptions

---

## Use Cases

- **Personalization** - Recommend content based on behavior
- **Product Analytics** - Understand user interests
- **Account Takeover Detection** - Stop slow and fast ATO attacks
- **Adaptive Authentication** - MFA only when behavior changes
- **Fraud Prevention** - Detect compromised accounts early
- **Post-Auth Surveillance** - Silent ongoing verification

---

## Architecture

### Database Setup

```python
sw = ShadowWatch(database_url="postgresql+asyncpg://localhost/db")
await sw.init_database()
```

**Tables created:**

- `shadow_watch_activity_events` - Raw activity log
- `shadow_watch_interests` - Aggregated interest scores
- `shadow_watch_library_versions` - Profile snapshots

---

## FastAPI Integration

```python
from fastapi import FastAPI, Request
from shadowwatch import ShadowWatch
import os

app = FastAPI()
sw = ShadowWatch(database_url=os.getenv("DATABASE_URL"))

@app.middleware("http")
async def track_activity_middleware(request: Request, call_next):
    if request.state.user:
        await sw.track(
            user_id=request.state.user.id,
            entity_id=request.url.path,
            action=request.method.lower()
        )
    return await call_next(request)

@app.post("/auth/login")
async def login(credentials: LoginRequest):
    user = await authenticate(credentials)
    if not user:
        return {"error": "Invalid credentials"}

    # ATO detection — check behavioral continuity
    continuity = await sw.calculate_continuity(str(user.id))

    if continuity["score"] < 0.4:
        return {"status": "mfa_required", "reason": "Low continuity"}
    elif continuity["score"] < 0.7:
        return {"status": "email_verification_required"}
    else:
        return {"status": "success", "token": generate_token(user)}
```

---

## Full API Reference

| Method                              | Description                           |
| ----------------------------------- | ------------------------------------- |
| `track(user_id, entity_id, action)` | Track user activity                   |
| `get_profile(user_id)`              | Get behavioral profile                |
| `get_library(user_id)`              | Get interest library                  |
| `verify_login(user_id, context)`    | Trust score for logins                |
| `calculate_continuity(subject_id)`  | Temporal actor persistence (ATO)      |
| `detect_divergence(subject_id)`     | Behavioral divergence _(coming soon)_ |
| `pre_auth_intent(identifier, obs)`  | Pre-auth analysis _(coming soon)_     |

---

## Documentation

- **[Getting Started](./docs/GETTING_STARTED.md)** - 5-minute setup guide
- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation
- **[Integration Guides](./docs/INTEGRATION_GUIDES.md)** - FastAPI, Django, Flask examples

---

## License

MIT License — free forever.

---

## Author

Built by [Tanishq](https://github.com/Tanishq1030) during development of [QuantForge Terminal](https://github.com/Tanishq1030/QuantForge-terminal)

**Questions?**

- Email: tanishqdasari2004@gmail.com
- GitHub: [github.com/Tanishq1030/Shadow_Watch](https://github.com/Tanishq1030/Shadow_Watch)

---

**"Always there. Never seen. Forever watching."** 🌑
