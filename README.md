# Shadow Watch

[![PyPI version](https://badge.fury.io/py/shadowwatch.svg)](https://badge.fury.io/py/shadowwatch)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**"Like a shadow — always there, never seen."**

Behavioral intelligence library for understanding user patterns. Choose your tier:

- **Free Tier** (MIT License) - Activity tracking & interest profiling
- **Pro Tier** (Commercial) - Account takeover detection & behavioral security

---

## 🆓 Free Tier

Track user activity and build interest profiles. **No license required.**

###Installation

```bash
pip install shadowwatch
```

### Quick Start

```python
from shadowwatch import ShadowWatch

# Initialize (no license needed)
sw = ShadowWatch(database_url="postgresql://localhost/db")

# Track activity
await sw.track(user_id=123, entity_id="AAPL", action="view")

# Get user profile
profile = await sw.get_profile(user_id=123)
# Returns: {"user_id": 123, "total_items": 10, "library": [...], "fingerprint": "abc123..."}

# Get interest library
library = await sw.get_library(user_id=123)
```

### Free Features

✅ **Activity Tracking** - Silent behavioral logging  
✅ **Interest Profiles** - Auto-generated from activity  
✅ **Behavioral Fingerprints** - Stable user signatures  
✅ **No Event Limits** - Track unlimited activities  
✅ **Self-Hosted** - Your data stays on your servers  

### Use Cases

- **Personalization** - Recommend content based on behavior
- **Product Analytics** - Understand user interests
- **Content Curation** - Auto-generate user preferences
- **Engagement Tracking** - Monitor activity patterns

---

## 🔐 Pro Tier

Advanced behavioral security features for detecting account takeovers and compromises.

### Installation

```bash
pip install shadowwatch-pro
```

### Get License

**Pricing:** Visit [shadowwatch.dev/pricing](https://shadowwatch.dev/pricing)  
**Trial:** Email tanishqdasari2004@gmail.com

### Quick Start

```python
from shadowwatch import ShadowWatch

# Initialize with Pro license
sw = ShadowWatch(
    license_key="SW-PRO-XXXX-XXXX-XXXX-XXXX",
    database_url="postgresql://localhost/db"
)

# All free features still work
await sw.track(user_id=123, entity_id="AAPL", action="view")

# Plus Pro features:

# Calculate temporal continuity
continuity = await sw.calculate_continuity("user_123")
# Returns: {"score": 0.82, "state": "stable", "confidence": 0.91}

# Detect behavioral divergence
divergence = await sw.detect_divergence("user_123")
# Returns: {"magnitude": 0.12, "mode": "none", "velocity": 0.03}

# Analyze pre-auth intent
intent = await sw.pre_auth_intent("user@example.com", {
    "navigation_path": ["/", "/login"],
    "time_to_submit": 120
})
# Returns: {"intent_score": 0.85, "confidence": 0.73}
```

### Pro Features

🔐 **Temporal Continuity Measurement** - Detect if current actor is still the account owner  
🔐 **Behavioral Divergence Detection** - Three attack modes (shock, creep, fracture)  
🔐 **Pre-Auth Intent Analysis** - Credential stuffing prevention  
🔐 **ATO Detection** - Slow and fast account takeover detection  
🔐 **Variance-Normalized** - Adapts to each user's unique patterns  

### Use Cases

- **Account Takeover Detection** - Stop slow and fast attacks
- **Adaptive Authentication** - MFA only when behavior changes
- **Fraud Prevention** - Detect compromised accounts early
- **Security Monitoring** - Continuous behavioral analysis
- **Post-Auth Surveillance** - Silent ongoing verification

---

## Architecture

### Free Tier Database (3 tables)

```bash
# Initialize database
sw = ShadowWatch(database_url="postgresql://localhost/db")
await sw.init_database()
```

**Tables created:**
- `shadow_watch_activity_events` - Raw activity log
- `shadow_watch_interests` - Aggregated interest scores
- `shadow_watch_library_versions` - Profile snapshots

### Pro Tier Database (4 additional tables)

```bash
# Run Pro migrations
python -m shadowwatch.storage.migrations.run_migrations "postgresql://localhost/db"
```

**Additional tables:**
- `continuity_state` - Behavioral state cache
- `divergence_history` - Historical divergence signals
- `feature_snapshots` - Variance calculation data
- `login_attempts` - Pre-auth event tracking

---

## Comparison

| Feature | Free Tier | Pro Tier |
|---------|-----------|----------|
| **Activity Tracking** | ✅ Unlimited | ✅ Unlimited |
| **Interest Profiles** | ✅ Auto-generated | ✅ Auto-generated |
| **Behavioral Fingerprints** | ✅ Included | ✅ Included |
| **Account Takeover Detection** | ❌ | ✅ Advanced |
| **Temporal Continuity** | ❌ | ✅ Real-time |
| **Divergence Detection** | ❌ | ✅ 3 attack modes |
| **Pre-Auth Analysis** | ❌ | ✅ Intent scoring |
| **License** | MIT (Open Source) | Commercial |
| **Price** | Free | $500-1500/month |
| **Support** | GitHub Issues | Priority Email |

---

## Integration Guides

### FastAPI Integration (Free Tier)

```python
from fastapi import FastAPI, Request
from shadowwatch import ShadowWatch

app = FastAPI()
sw = ShadowWatch(database_url="postgresql://localhost/db")

@app.middleware("http")
async def track_activity_middleware(request: Request, call_next):
    # Track all user activity silently
    if request.state.user:
        await sw.track(
            user_id=request.state.user.id,
            entity_id=request.url.path,
            action=request.method.lower()
        )
    return await call_next(request)
```

### FastAPI Integration (Pro Tier)

```python
from shadowwatch import ShadowWatch, LicenseError

sw = ShadowWatch(
    license_key="SW-PRO-...",
    database_url="postgresql://localhost/db"
)

@app.post("/auth/login")
async def login(credentials: LoginRequest):
    # Your normal auth
    user = await authenticate(credentials)
    if not user:
        return {"error": "Invalid credentials"}
    
    # Check behavioral continuity (Pro)
    try:
        continuity = await sw.calculate_continuity(str(user.id))
        
        if continuity["score"] < 0.4:
            return {"status": "mfa_required", "reason": "Low continuity"}
        elif continuity["score"] < 0.7:
            return {"status": "email_verification_required"}
        else:
            return {"status": "success", "token": generate_token(user)}
    
    except LicenseError:
        # Graceful degradation if Pro not available
        return {"status": "success", "token": generate_token(user)}
```

---

## Documentation

- **[Getting Started](./docs/GETTING_STARTED.md)** - 5-minute setup guide
- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation
- **[Integration Guides](./docs/INTEGRATION_GUIDES.md)** - FastAPI, Django, Flask examples
- **[Pro Features Guide](./docs/PRO_FEATURES.md)** - Advanced security features *(coming soon)*

---

## Pricing

### Free Tier
- **Price:** $0
- **Events:** Unlimited
- **Features:** Activity tracking, interest profiles, fingerprints
- **License:** MIT (Open Source)
- **Support:** GitHub Issues

### Pro Tier

| Plan | Price | Events/Month | Support |
|------|-------|--------------|---------|
| Startup | $500/month | 100,000 | Priority Email |
| Growth | $1,500/month | 1,000,000 | Slack Channel |
| Enterprise | Custom | Unlimited | Dedicated Support |

**For trial license:** Email tanishqdasari2004@gmail.com

---

## FAQ

### Can I use the free tier in production?
**Yes!** Free tier is MIT licensed and has no event limits.

### What happens if I call Pro methods without a license?
You get a helpful `LicenseError` with installation instructions. Your app keeps working - Pro methods just raise an exception.

### Can I upgrade from free to Pro later?
**Absolutely.** Just add the `license_key` parameter. All your existing data stays intact.

### Do I need shadowwatch-pro installed for free tier?
**No.** Free tier works standalone. Only install `shadowwatch-pro` if you have a Pro license.

### Is my data sent to Shadow Watch servers?
**Never.** Everything runs on your infrastructure. Free or Pro.

---

## License

- **Free Tier:** MIT License (Open Source)
- **Pro Tier:** Commercial License

---

## Author

Built by [Tanishq](https://github.com/Tanishq1030) during development of [QuantForge Terminal](https://github.com/Tanishq1030/QuantForge-terminal)

**Questions?**
- Email: tanishqdasari2004@gmail.com
- GitHub: [github.com/Tanishq1030/Shadow_Watch](https://github.com/Tanishq1030/Shadow_Watch)

---

**"Always there. Never seen. Forever watching."** 🌑
