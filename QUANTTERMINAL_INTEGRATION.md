# Shadow Watch → QuantTerminal Integration Plan

## Goal: Real-World Testing Before v1.0

Use QuantTerminal as the first production customer to verify all Shadow Watch features work as expected.

---

## Phase 1: PostgreSQL Integration (Critical)

### Setup Database

```bash
# QuantTerminal already has PostgreSQL, right?
# Use existing connection or create shadow_watch schema

# Option 1: Separate schema
CREATE SCHEMA shadow_watch;

# Option 2: Shared database with prefix
# Use table naming: quantforge_shadow_watch_*
```

### Integration Code

```python
# In QuantTerminal backend
from shadowwatch import ShadowWatch

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url=settings.DATABASE_URL,  # Your PostgreSQL connection
    license_key=None,  # Local dev mode first, then production license
    redis_url=settings.REDIS_URL  # Your existing Redis
)

# On startup
@app.on_event("startup")
async def init_shadow_watch():
    await sw.init_database()
    logger.info("✅ Shadow Watch initialized")
```

### What to Track

**Stock/Asset Views:**
```python
# When user views stock details
await sw.track(
    user_id=current_user.id,
    entity_id=stock_symbol,  # "AAPL", "MSFT", etc.
    action="view",
    metadata={"source": "dashboard", "duration_seconds": 45}
)
```

**Trade Activity:**
```python
# When user executes trade
await sw.track(
    user_id=current_user.id,
    entity_id=stock_symbol,
    action="trade",
    metadata={
        "type": "buy",
        "quantity": 100,
        "price": 150.25
    }
)
```

**Watchlist Management:**
```python
# When user adds to watchlist
await sw.track(
    user_id=current_user.id,
    entity_id=stock_symbol,
    action="watchlist",
    metadata={"action": "add"}
)
```

**Portfolio Analysis:**
```python
# When user analyzes portfolio
await sw.track(
    user_id=current_user.id,
    entity_id="portfolio_tech",
    action="analyze",
    metadata={"type": "sector_analysis"}
)
```

---

## Phase 2: Feature Testing

### Test 1: Behavioral Profiles

```python
# Get user's stock interests
profile = await sw.get_profile(user_id=current_user.id)

# Use for recommendations
top_stocks = [item['entity_id'] for item in profile['library'][:5]]
recommendation_engine.suggest_similar(top_stocks)
```

### Test 2: Fraud Detection

```python
# On login
trust_result = await sw.verify_login(
    user_id=current_user.id,
    request_context={
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "device_fingerprint": get_device_id(request)
    }
)

if trust_result['trust_score'] < 0.5:
    # Suspicious login!
    logger.warning(f"Low trust score for user {current_user.id}")
    # Require 2FA or email verification
```

### Test 3: Interest-Based Features

```python
# Use Shadow Watch profile to:
# 1. Personalize dashboard (show stocks they care about)
# 2. Smart notifications (only for stocks they watch)
# 3. Onboarding shortcuts (skip irrelevant sectors)

interests = await sw.get_profile(user_id=new_user.id)
if not interests['library']:
    # New user - show onboarding
    show_welcome_tour()
else:
    # Returning user - show their portfolio
    show_personalized_dashboard(interests['library'])
```

---

## Phase 3: Load Testing

### Generate Test Data

```python
# Script to simulate realistic usage
import asyncio
from shadowwatch import ShadowWatch

async def simulate_users(num_users=100, events_per_user=100):
    sw = ShadowWatch(
        database_url="postgresql+asyncpg://...",
        license_key="SW-PROD-YOUR-KEY"
    )
    
    stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"]
    
    for user_id in range(1, num_users + 1):
        for _ in range(events_per_user):
            stock = random.choice(stocks)
            action = random.choice(["view", "trade", "watchlist"])
            
            await sw.track(user_id, stock, action)
        
        if user_id % 10 == 0:
            print(f"Processed {user_id} users...")
    
    print(f"\n✅ Generated {num_users * events_per_user} events")

# Run load test
asyncio.run(simulate_users(100, 100))  # 10,000 events
```

### Monitor Performance

```python
# Check response times
import time

start = time.time()
await sw.track(user_id=1, entity_id="AAPL", action="view")
elapsed = time.time() - start

print(f"Track time: {elapsed*1000:.2f}ms")
# Should be < 50ms for PostgreSQL
```

---

## Phase 4: License Server Testing

### Step 1: Generate Production License

```python
# Use your admin script
license_key = await generate_production_license(
    company="QuantTerminal",
    contact_email="your@email.com",
    event_limit=None,  # Unlimited
    valid_days=365
)

print(f"License: {license_key}")
```

### Step 2: Update QuantTerminal Config

```python
# .env
SHADOWWATCH_LICENSE_KEY=SW-PROD-XXXX-XXXX-XXXX-XXXX
```

### Step 3: Verify License Works

```python
# Should NOT show "LOCAL DEV MODE" warning
# Should NOT have event limit
assert not sw._local_mode
assert sw._event_limit is None
```

---

## Phase 5: Multi-Instance Testing

### Setup

```bash
# Run multiple QuantTerminal instances
# All pointing to same Redis

# Instance 1
uvicorn app:main --port 8000

# Instance 2
uvicorn app:main --port 8001

# Instance 3
uvicorn app:main --port 8002
```

### Test Cache Sharing

```python
# Track event on instance 1
# Verify cache hit on instance 2

# Instance 1:
await sw.track(user_id=123, entity_id="AAPL", action="view")

# Instance 2 (should use cached license):
await sw.track(user_id=456, entity_id="MSFT", action="view")
# Should be fast (cache hit)
```

---

## Phase 6: Admin Dashboard (Basic)

### Create Monitoring Script

```python
# admin_monitor.py
import streamlit as st
import asyncio
from shadowwatch import ShadowWatch

st.title("QuantTerminal - Shadow Watch Monitoring")

# Show current usage
sw = ShadowWatch(...)  # Your connection

# Get stats
total_users = st.number_input("Total users tracked", value=1500)
total_events = st.number_input("Total events", value=45000)

st.metric("Events/User", total_events / total_users)

# Show top stocks
st.subheader("Most Tracked Stocks")
# Query your database
# SELECT entity_id, COUNT(*) FROM shadow_watch_activities GROUP BY entity_id ORDER BY count DESC LIMIT 10
```

---

## Testing Checklist

### PostgreSQL Integration
- [ ] Shadow Watch initializes with PostgreSQL
- [ ] Tables created successfully
- [ ] Events tracked across sessions
- [ ] Profiles retrieved correctly
- [ ] No "table not found" errors
- [ ] Performance acceptable (< 50ms per track)

### License Flow
- [ ] Production license generated
- [ ] License validates on server
- [ ] No event limit enforced
- [ ] Redis cache works
- [ ] Multi-instance caching works

### Load Testing
- [ ] 10,000+ events tracked
- [ ] No performance degradation
- [ ] Database queries optimized
- [ ] Redis cache hit rate > 80%

### Features
- [ ] Behavioral profiles accurate
- [ ] Trust scores calculated
- [ ] Fingerprinting works
- [ ] Recommendations improve

### Monitoring
- [ ] Can track usage metrics
- [ ] Can identify top users
- [ ] Can see most tracked stocks
- [ ] License status visible

---

## Success Criteria for v1.0

✅ **All PostgreSQL tests pass**  
✅ **10,000+ events tracked in QuantTerminal**  
✅ **Production license works**  
✅ **Multi-instance caching verified**  
✅ **Performance acceptable (< 50ms/event)**  
✅ **No critical bugs found**  
✅ **QuantTerminal users benefit from features**

**When all checked → Ship v1.0! 🚀**

---

## Timeline Estimate

**Day 1-2:** PostgreSQL integration + basic tracking  
**Day 3:** Feature testing (profiles, trust scores)  
**Day 4:** Load testing + optimization  
**Day 5:** Admin dashboard + monitoring  
**Day 6:** Final checklist + v1.0 release

**Total: ~1 week of testing**

---

## Next Immediate Steps

1. **Get QuantTerminal database connection string**
2. **Generate production license for QuantTerminal**
3. **Add Shadow Watch to QuantTerminal requirements**
4. **Initialize Shadow Watch in QuantTerminal startup**
5. **Start tracking stock views**

**Ready to start integrating?** 🚀
