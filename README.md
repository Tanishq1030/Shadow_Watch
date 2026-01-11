# Shadow Watch

[![PyPI version](https://badge.fury.io/py/shadowwatch.svg)](https://badge.fury.io/py/shadowwatch)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/shadowwatch)](https://pepy.tech/project/shadowwatch)

**"Like a shadow — always there, never seen."**

Behavioral intelligence for your application. Add passive behavioral biometrics, personalization, and fraud detection with zero user friction.

## What It Does

Shadow Watch silently learns user behavior patterns and uses them for:

- **🔐 Security:** Behavioral biometric authentication (detects account takeovers)
- **🎯 Personalization:** Auto-generates interest profiles based on activity
- **🤖 Intent Prediction:** Understands what users care about without asking
- **🚨 Fraud Detection:** Flags suspicious behavior before damage happens

## Installation

```bash
# Basic installation
pip install shadowwatch

# With Redis support (recommended for production)
pip install shadowwatch[redis]

# With FastAPI integration
pip install shadowwatch[fastapi]
```

**Get your free trial license:** Email tanishqdasari2004@gmail.com or visit the [license server](https://shadow-watch-three.vercel.app)

## Quick Start

```python
from shadowwatch import ShadowWatch

# Initialize with your database
sw = ShadowWatch(
    database_url="postgresql+asyncpg://user:pass@localhost/db",
    license_key="SW-TRIAL-XXXX-XXXX-XXXX"  # Get trial at shadowwatch.dev
)

# Track user activity (silent, no UI)
await sw.track(
    user_id=123,
    entity_id="AAPL",
    action="view"
)

# Get user profile
profile = await sw.get_profile(user_id=123)
# Returns: {"total_items": 42, "fingerprint": "a7f9e2c4...", "library": [...]}

# Verify login (trust score)
trust = await sw.verify_login(
    user_id=123,
    request_context={
        "ip": "192.168.1.1",
        "user_agent": "...",
        "library_fingerprint": "..."  # From client cache
    }
)
# Returns: {"trust_score": 0.85, "risk_level": "low", "action": "allow"}
```

## How It Works

1. **Silent Tracking:** Every user action (views, searches, trades) is logged
2. **Interest Scoring:** Actions aggregate into weighted interest scores
3. **Fingerprinting:** Top interests generate a unique behavioral fingerprint
4. **Trust Calculation:** Fingerprint mismatch = suspicious login attempt

## Use Cases

### Fintech Apps
- Detect account takeover attempts
- Behavioral 2FA (no user friction)
- Portfolio-aware personalization

### E-commerce
- Predict purchase intent
- Fraud detection
- Product recommendations

### Trading Platforms
- Smart watchlists
- Pattern-based alerts
- Risk profiling

## Features

✅ **Zero User Friction** - Works silently, no prompts  
✅ **Passive Authentication** - Behavioral biometric layer  
✅ **Auto-Generated Profiles** - based on actual behavior  
✅ **Investment Priority** - Trades weighted 10x higher than views  
✅ **Self-Hosted** - Runs on YOUR infrastructure  
✅ **Privacy-First** - Your data never leaves your servers  

## Database Setup

Shadow Watch uses 3 tables:

```bash
# Create tables (SQLAlchemy)
from shadowwatch.models import Base
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

Tables created:
- `shadow_watch_activity_events` (raw events)
- `shadow_watch_interests` (aggregated scores)
- `shadow_watch_library_versions` (snapshots)

## Pricing

| Tier | Price | Events/Month | Support |
|------|-------|--------------|---------|
| Trial | Free (30 days) | 10,000 | Email |
| Startup | $500/month | 100,000 | Priority |
| Growth | $1,500/month | 1,000,000 | Slack |
| Enterprise | Custom | Unlimited | Dedicated |

**For trial license:** tanishqdasari2004@gmail.com  

## Documentation

- [Getting Started Guide](./docs/GETTING_STARTED.md) - 5-minute setup
- [API Reference](./docs/API_REFERENCE.md) - Complete API documentation
- [Integration Guides](./docs/INTEGRATION_GUIDES.md) - FastAPI, Django, Flask

## Comparison

| Feature | Traditional 2FA | Shadow Watch |
|---------|----------------|--------------|
| User Friction | High (SMS, app) | **Zero (passive)** |
| Hackable | Yes (SIM swap) | **No (behavioral)** |
| Setup Time | Weeks | **5 lines of code** |
| Personalization | None | **Auto-generated** |

## License

MIT License - see [LICENSE](./LICENSE)

## Author

Built by [Tanishq](https://github.com/Tanishq1030) during development of [QuantForge Terminal](https://github.com/Tanishq1030/QuantForge-terminal)

## Questions?

- Email: tanishqdasari2004@gmail.com
- GitHub Issues: [github.com/Tanishq1030/Shadow_Watch/issues](https://github.com/Tanishq1030/Shadow_Watch/issues)

---

**"Always there. Never seen. Forever watching."** 🌑
