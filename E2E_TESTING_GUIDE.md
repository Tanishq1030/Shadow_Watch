# Shadow Watch - End-to-End Testing Guide

## Overview

This guide walks through the complete Shadow Watch ecosystem from **two perspectives**:

1. **CLIENT SIDE** - How developers integrate Shadow Watch into their apps
2. **PROVIDER SIDE** - How you (admin) manage licenses and monitor usage

---

# PART 1: CLIENT SIDE (Library User)

## Scenario: E-commerce Company Wants to Add Shadow Watch

### Step 1: Discovery & Trial Request

**Developer finds Shadow Watch:**
- GitHub: https://github.com/Tanishq1030/Shadow_Watch
- PyPI: https://pypi.org/project/shadowwatch/
- Docs: https://shadow-watch-three.vercel.app

**Get trial license:**

**Option A: Self-Service (Instant)**
```bash
# Visit trial page
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@techshop.com",
    "company": "TechShop Inc",
    "use_case": "Product recommendations for e-commerce site"
  }'

# Response:
{
  "license_key": "SW-TRIAL-XXXX-XXXX-XXXX",
  "tier": "trial",
  "expires": "2026-02-10",
  "event_limit": 10000,
  "message": "Trial license generated! Valid for 30 days."
}
```

**Option B: Email Request**
```
To: tanishqdasari2004@gmail.com
Subject: Shadow Watch Trial Request

Hi, I'd like to try Shadow Watch for our e-commerce platform.

Company: TechShop Inc
Use Case: Product recommendations
Expected Volume: 50,000 events/month

Thanks!
John Doe
john@techshop.com
```

---

### Step 2: Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Shadow Watch
pip install shadowwatch

# Install database driver (choose one)
pip install asyncpg  # PostgreSQL (recommended)
pip install aiomysql  # MySQL
pip install aiosqlite  # SQLite (demo/testing only - will show warning)

# Install Redis for multi-instance caching (optional but recommended)
pip install redis
```

---

### Step 3: Database Setup

**PostgreSQL (Recommended):**
```bash
# Create database
psql -U postgres -c "CREATE DATABASE ecommerce_prod;"

# Connection string
postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_prod
```

**MySQL:**
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE ecommerce_prod;"

# Connection string
mysql+aiomysql://root:password@localhost:3306/ecommerce_prod
```

---

### Step 4: Integration into Application

**Example: FastAPI E-commerce App**

```python
# app.py
from fastapi import FastAPI, Depends
from shadowwatch import ShadowWatch
from shadowwatch.integrations.fastapi import ShadowWatchMiddleware

app = FastAPI()

# Initialize Shadow Watch
sw = ShadowWatch(
    database_url="postgresql+asyncpg://postgres:password@localhost/ecommerce_prod",
    license_key="SW-TRIAL-XXXX-XXXX-XXXX",  # Your trial key
    redis_url="redis://localhost:6379/0"  # Optional but recommended
)

# Add middleware for automatic tracking
app.add_middleware(
    ShadowWatchMiddleware,
    shadowwatch=sw,
    track_paths=["/products", "/cart", "/checkout"]  # Routes to track
)

# Initialize database (run once on startup)
@app.on_event("startup")
async def startup():
    await sw.init_database()
    print("✅ Shadow Watch initialized")

# Manual tracking example
@app.post("/products/{product_id}/view")
async def track_product_view(product_id: str, user_id: int):
    # Track product view
    await sw.track(
        user_id=user_id,
        entity_id=product_id,
        action="view",
        metadata={"source": "search_results"}
    )
    return {"status": "tracked"}

# Get user recommendations
@app.get("/users/{user_id}/recommendations")
async def get_recommendations(user_id: int):
    # Get user's behavioral profile
    profile = await sw.get_profile(user_id=user_id)
    
    # Use profile to generate recommendations
    interests = [item['entity_id'] for item in profile['library'][:5]]
    
    return {
        "recommended_products": interests,
        "reason": "Based on your browsing history"
    }

# Fraud detection example
@app.post("/checkout")
async def checkout(user_id: int, request_data: dict):
    # Verify this looks like the real user
    trust_result = await sw.verify_login(
        user_id=user_id,
        request_context={
            "ip_address": request_data.get("ip"),
            "user_agent": request_data.get("user_agent"),
            "device_fingerprint": request_data.get("device_id")
        }
    )
    
    if trust_result['trust_score'] < 0.5:
        # Suspicious! Require 2FA
        return {"status": "2fa_required", "reason": "Unusual login pattern"}
    
    # Process checkout...
    return {"status": "success"}
```

---

### Step 5: Run & Test

```bash
# Start application
uvicorn app:main --reload

# Test tracking
curl -X POST http://localhost:8000/products/laptop_dell/view \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'

# Get recommendations
curl http://localhost:8000/users/123/recommendations

# Response:
{
  "recommended_products": ["laptop_dell", "mouse_wireless"],
  "reason": "Based on your browsing history"
}
```

---

### Step 6: Monitor Usage (Client Side)

**Check event count:**
```python
# In your app
current_usage = sw._event_count
limit = sw._event_limit

print(f"Events used: {current_usage}/{limit}")

if current_usage > limit * 0.8:
    # Alert: Approaching limit!
    print("⚠️ 80% of event limit reached - upgrade soon!")
```

---

### Step 7: Upgrade to Production

**When trial expires or limit reached:**

1. Email: tanishqdasari2004@gmail.com
2. Subject: "Shadow Watch Production License - [Company Name]"
3. Provide:
   - Company details
   - Expected monthly volume
   - Use case summary

**Receive production license:**
```
SW-PROD-XXXX-XXXX-XXXX-XXXX
```

**Update .env:**
```bash
SHADOWWATCH_LICENSE_KEY=SW-PROD-XXXX-XXXX-XXXX-XXXX
```

---

# PART 2: PROVIDER SIDE (Your Admin View)

## Managing Licenses & Monitoring Usage

### Step 1: Access License Server

**Your license server:**
```
URL: https://shadow-watch-three.vercel.app
Admin: You (via Vercel dashboard + direct API access)
```

---

### Step 2: Generate Trial License (Self-Service Endpoint)

**Endpoint already deployed:**
```bash
POST /trial
```

**Test it:**
```bash
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "company": "Test Corp",
    "use_case": "Testing Shadow Watch"
  }'
```

**What happens:**
1. Generates unique trial key: `SW-TRIAL-{uuid}`
2. Stores in Vercel KV with 30-day expiry
3. Returns license to client immediately

---

### Step 3: Generate Production License (Manual)

**Create admin script:**

```python
# generate_prod_license.py
import httpx
import secrets
from datetime import datetime, timedelta

async def generate_production_license(
    company: str,
    contact_email: str,
    event_limit: int = None,  # None = unlimited
    valid_days: int = 365
):
    """Generate production license manually"""
    
    # Generate unique license key
    license_key = f"SW-PROD-{secrets.token_hex(8).upper()}"
    
    # Calculate expiry
    expires = (datetime.now() + timedelta(days=valid_days)).isoformat()
    
    # License data
    license_data = {
        "key": license_key,
        "tier": "production",
        "customer": company,
        "contact": contact_email,
        "event_limit": event_limit,  # None = unlimited
        "expires": expires,
        "created": datetime.now().isoformat()
    }
    
    # Store in Vercel KV (requires admin access)
    # Option 1: Via Vercel API
    async with httpx.AsyncClient() as client:
        await client.put(
            f"https://api.vercel.com/v1/kv/projects/YOUR_PROJECT_ID/keys/{license_key}",
            headers={"Authorization": f"Bearer {VERCEL_TOKEN}"},
            json=license_data
        )
    
    # Option 2: Direct Redis connection (if you have Redis locally)
    # redis_client.setex(license_key, ttl, json.dumps(license_data))
    
    print(f"\n✅ Production License Generated:")
    print(f"   License Key: {license_key}")
    print(f"   Customer: {company}")
    print(f"   Event Limit: {'Unlimited' if event_limit is None else event_limit}")
    print(f"   Valid Until: {expires}")
    print(f"\n📧 Send to: {contact_email}")
    
    return license_key

# Usage
if __name__ == "__main__":
    import asyncio
    
    license = asyncio.run(generate_production_license(
        company="TechShop Inc",
        contact_email="john@techshop.com",
        event_limit=None,  # Unlimited for production
        valid_days=365  # 1 year
    ))
```

---

### Step 4: Monitor Client Usage

**Create monitoring dashboard script:**

```python
# monitor_usage.py
import httpx
from datetime import datetime

async def get_license_stats(license_key: str):
    """Check license status and usage"""
    
    # Call verify endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://shadow-watch-three.vercel.app/verify",
            json={"license_key": license_key}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 License Status: {license_key}")
            print(f"   Tier: {data.get('tier')}")
            print(f"   Customer: {data.get('customer')}")
            print(f"   Valid: {data.get('valid')}")
            print(f"   Event Limit: {data.get('event_limit', 'Unlimited')}")
            print(f"   Events Used: {data.get('events_used', 'Not tracked')}")
            print(f"   Expires: {data.get('expires')}")
            
            # Check if approaching limits
            if data.get('event_limit'):
                used = data.get('events_used', 0)
                limit = data['event_limit']
                percentage = (used / limit) * 100
                
                if percentage > 80:
                    print(f"   ⚠️  WARNING: {percentage:.1f}% of limit used!")
                    print(f"   💡 Consider contacting customer about upgrade")
        else:
            print(f"❌ License not found or invalid")

# Monitor all active licenses
async def monitor_all_licenses():
    """Check all active licenses"""
    
    # Would need to query Vercel KV for all keys
    # Or maintain a separate database of issued licenses
    
    licenses = [
        "SW-TRIAL-XXXX-XXXX-XXXX",
        "SW-PROD-XXXX-XXXX-XXXX",
    ]
    
    for license_key in licenses:
        await get_license_stats(license_key)
        print("-" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(monitor_all_licenses())
```

---

### Step 5: Usage Tracking (Advanced)

**Add usage reporting to license server:**

```python
# In license_server/main.py

@app.post("/usage/report")
async def report_usage(
    license_key: str,
    events_count: int,
    timestamp: str
):
    """Clients report their usage periodically"""
    
    # Verify license
    license_data = await kv_store.get(license_key)
    if not license_data:
        raise HTTPException(404, "Invalid license")
    
    # Update usage counter
    current_usage = license_data.get("events_used", 0)
    license_data["events_used"] = current_usage + events_count
    license_data["last_reported"] = timestamp
    
    # Save back to KV
    await kv_store.set(license_key, license_data)
    
    # Check if approaching limit
    limit = license_data.get("event_limit")
    if limit and (current_usage + events_count) > limit * 0.9:
        # Alert! Customer approaching limit
        # Could send email notification here
        pass
    
    return {"status": "recorded", "total_events": current_usage + events_count}
```

---

### Step 6: Analytics Dashboard (Future)

**Create admin dashboard (Streamlit example):**

```python
# dashboard.py
import streamlit as st
import pandas as pd

st.title("Shadow Watch - Admin Dashboard")

# Fetch all licenses from KV
licenses_df = pd.DataFrame([
    {"Customer": "TechShop Inc", "Tier": "production", "Events": 45000, "Limit": "Unlimited", "Status": "Active"},
    {"Customer": "GameCo", "Tier": "trial", "Events": 8500, "Limit": 10000, "Status": "Active"},
    {"Customer": "SocialApp", "Tier": "trial", "Events": 9800, "Limit": 10000, "Status": "⚠️ Near Limit"},
])

st.dataframe(licenses_df)

# Charts
st.bar_chart(licenses_df.set_index("Customer")["Events"])

# Alerts
st.subheader("⚠️ Alerts")
near_limit = licenses_df[licenses_df["Status"].str.contains("Near")]
st.write(f"{len(near_limit)} customers approaching trial limits")
```

---

## Testing Checklist

### Client Side Tests

- [ ] Install shadowwatch via pip
- [ ] Request trial license (self-service)
- [ ] Initialize ShadowWatch with trial key
- [ ] Create database tables (`init_database()`)
- [ ] Track events (view, purchase, etc.)
- [ ] Get user profile
- [ ] Verify fraud detection
- [ ] Monitor event usage
- [ ] Upgrade to production license

### Provider Side Tests

- [ ] Generate trial license via `/trial` endpoint
- [ ] Verify trial license works for client
- [ ] Generate production license manually
- [ ] Monitor license usage
- [ ] Check approaching limits
- [ ] Revoke/expire licenses
- [ ] Handle license validation errors

---

## Quick Test Script

**Run this end-to-end test:**

```bash
# 1. Install
pip install shadowwatch asyncpg

# 2. Request trial
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "test@test.com", "company": "Test", "use_case": "Testing"}'

# 3. Use the license key from response in app
# (See Step 4 above)

# 4. Monitor usage (provider side)
# (See Step 4 in Provider section)
```

---

## Success Criteria

✅ Client can get trial instantly  
✅ Client can integrate in < 30 minutes  
✅ Tracking works across industries  
✅ You can generate production licenses  
✅ You can monitor usage  
✅ System scales to multiple clients  

---

**Ready to test?** Start with Step 1 (Client Side) and work through the flow!
