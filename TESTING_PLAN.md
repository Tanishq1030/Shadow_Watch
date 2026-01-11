# Shadow Watch - Comprehensive Testing Plan

## Testing Strategy

**Goal:** Verify all Shadow Watch v0.3.0 features work correctly with PostgreSQL

**Why PostgreSQL:** SQLite async has known schema propagation issues. PostgreSQL is the production recommendation.

---

## Test Setup Options

### Option 1: Docker PostgreSQL (Recommended)
```bash
# Start PostgreSQL in Docker
docker run --name postgres-test \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=shadowwatch_test \
  -p 5432:5432 \
  -d postgres:15

# Connection string
postgresql+asyncpg://postgres:testpass@localhost:5432/shadowwatch_test
```

### Option 2: Local PostgreSQL Installation
```bash
# Windows (if installed)
# Set password, create database
psql -U postgres -c "CREATE DATABASE shadowwatch_test;"
```

### Option 3: Skip Database Tests (Document Only)
- Test validators, imports, initialization
- Verify warnings work
- Document that DB tests require PostgreSQL

---

## Test Checklist

### ✅ Core Functionality Tests

1. **License-Optional Mode**
   - [x] Initialize with `license_key=None`
   - [x] Verify 1000 event limit set
   - [x] Verify warning message displays

2. **SQLite Guardrail**
   - [x] Verify warning appears for sqlite+aiosqlite
   - [x] Verify PostgreSQL doesn't show warning

3. **Validators (Universal)**
   - [ ] Test custom actions (e-commerce, gaming, social)
   - [ ] Test deprecated actions (alert_set → alert)
   - [ ] Test get_action_weight()
   - [ ] Test flexible entity_id (no uppercase forcing)

4. **Imports**
   - [x] All modules import correctly
   - [x] STANDARD_ACTIONS available
   - [x] get_action_weight available

---

### 🗄️ Database Tests (PostgreSQL Required)

5. **Table Creation**
   - [ ] `init_database()` creates all tables
   - [ ] Tables visible to new sessions
   - [ ] No schema propagation issues

6. **Activity Tracking**
   - [ ] Track custom actions (purchase, like, equip)
   - [ ] Metadata storage works
   - [ ] Event counter increments

7. **Profile Generation**
   - [ ] `get_profile()` returns interest library
   - [ ] Score calculation works
   - [ ] Multiple entities tracked

8. **Multi-Industry Examples**
   - [ ] E-commerce flow works
   - [ ] Gaming flow works
   - [ ] Social media flow works

---

### 🔒 Security Tests (Advanced)

9. **Trust Score**
   - [ ] Calculate trust score for user
   - [ ] Fingerprint generation
   - [ ] Anomaly detection

10. **License Verification**
    - [ ] Trial license validation
    - [ ] License caching works
    - [ ] Event limit enforcement

---

## Quick Test Script (No DB Required)

```python
# Test validators and imports
from shadowwatch.utils.validators import (
    validate_action,
    get_action_weight,
    STANDARD_ACTIONS
)

# Test custom actions
assert validate_action("purchase") == "purchase"  # E-commerce
assert validate_action("like") == "like"  # Social media
assert validate_action("equip") == "equip"  # Gaming

# Test weights
assert get_action_weight("trade") == 10  # Highest
assert get_action_weight("view") == 1    # Lowest
assert get_action_weight("custom") == 1  # Default

# Test deprecated (with warning)
assert validate_action("alert_set") == "alert"  # Converts

print("✅ All validator tests passed!")
```

---

## Integration Test (PostgreSQL Required)

```python
import asyncio
from shadowwatch import ShadowWatch

async def test_full_flow():
    # Initialize with PostgreSQL
    sw = ShadowWatch(
        database_url="postgresql+asyncpg://postgres:testpass@localhost/shadowwatch_test",
        license_key=None  # Local dev mode
    )
    
    # Create tables
    await sw.init_database()
    
    # Test multi-industry tracking
    user_id = 123
    
    # E-commerce
    await sw.track(user_id, "laptop_dell", "view")
    await sw.track(user_id, "laptop_dell", "purchase")
    
    # Gaming
    await sw.track(user_id, "character_warrior", "select")
    await sw.track(user_id, "sword_legendary", "equip")
    
    # Social media
    await sw.track(user_id, "post_tech_news", "like")
    
    # Get profile
    profile = await sw.get_profile(user_id)
    
    print(f"✅ Tracked {len(profile['library'])} entities")
    print(f"✅ Event count: {sw._event_count}/1000")
    
    assert len(profile['library']) == 5
    assert sw._event_count == 5
    
    print("✅ Full integration test passed!")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
```

---

## Test Results (To Be Filled)

### Validator Tests
- [ ] Custom actions: PASS/FAIL
- [ ] Weights: PASS/FAIL
- [ ] Deprecated: PASS/FAIL

### PostgreSQL Tests
- [ ] Table creation: PASS/FAIL
- [ ] Tracking: PASS/FAIL
- [ ] Profiles: PASS/FAIL
- [ ] Multi-industry: PASS/FAIL

### Example Scripts
- [ ] E-commerce: PASS/FAIL
- [ ] Gaming: PASS/FAIL
- [ ] Social media: PASS/FAIL

---

## Decision Point

**Do you have PostgreSQL available?**

**YES** → Run full integration tests  
**NO** → Run validator tests only, document PostgreSQL requirement

**Alternative:** Deploy to Heroku/Railway with free PostgreSQL tier for testing
