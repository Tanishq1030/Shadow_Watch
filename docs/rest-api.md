# Shadow Watch REST API Reference

Base URL: **`https://shadow-watch-three.vercel.app`**

All endpoints return JSON responses.

---

## 📍 Public Endpoints

### 1. `GET /`

**Health check and service info**

```bash
curl https://shadow-watch-three.vercel.app/
```

**Response:**
```json
{
  "service": "Shadow Watch License Server",
  "status": "operational",
  "version": "2.1.0",
  "storage": {
    "redis": true,
    "supabase": true,
    "memory": true
  }
}
```

---

### 2. `GET /health`

**Detailed health check**

```bash
curl https://shadow-watch-three.vercel.app/health
```

**Response:**
```json
{
  "status": "operational",
  "storage": {
    "redis": "connected",
    "supabase": "connected",
    "memory": "connected"
  }
}
```

---

### 3. `POST /trial`

**Generate 30-day trial license key**

**Request:**
```bash
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Acme Inc"
  }'
```

**Request Body:**
```typescript
{
  name: string;      // Your name
  email: string;     // Your email
  company?: string;  // Optional (default: "Individual")
}
```

**Response (Success):**
```json
{
  "success": true,
  "license_key": "SW-TRIAL-A3F2C1B4E5D6F7A8",
  "expires_at": "2026-02-12T12:00:00.000Z",
  "max_events": 10000,
  "tier": "trial",
  "message": "30-day trial activated",
  "storage_used": {
    "redis": true,
    "supabase": true,
    "memory": true
  }
}
```

**Response (Error):**
```json
{
  "detail": "Failed to generate trial: <error message>"
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### 4. `GET /verify/{license_key}`

**Verify license key validity**

**Request:**
```bash
curl https://shadow-watch-three.vercel.app/verify/SW-TRIAL-A3F2C1B4E5D6F7A8
```

**Response (Valid):**
```json
{
  "valid": true,
  "tier": "trial",
  "events_used": 523,
  "max_events": 10000,
  "expires_at": "2026-02-12T12:00:00.000Z"
}
```

**Response (Invalid):**
```json
{
  "valid": false,
  "reason": "expired"  // or "not_found", "limit_reached", "revoked", "invalid_data"
}
```

**Invalid Reasons:**
- `not_found` - License key doesn't exist
- `expired` - License has expired
- `limit_reached` - Event limit exceeded (10,000 for trial)
- `revoked` - License manually deactivated
- `invalid_data` - Corrupted license data

**Status Codes:**
- `200` - Always (check `valid` field)

---

### 5. `GET /stats`

**Get license statistics**

```bash
curl https://shadow-watch-three.vercel.app/stats
```

**Response:**
```json
{
  "total_licenses": 142,
  "active_licenses": 98,
  "expired_licenses": 44,
  "storage": {
    "redis": true,
    "supabase": true,
    "memory": true
  }
}
```

**Status Codes:**
- `200` - Success

---

### 6. `GET /licenses`

**List all licenses (Admin Dashboard)**

```bash
curl https://shadow-watch-three.vercel.app/licenses
```

**Response:**
```json
{
  "total": 142,
  "licenses": [
    {
      "license_key": "SW-TRIAL-A3F2C1B4E5D6F7A8",
      "tier": "trial",
      "max_events": 10000,
      "events_used": 523,
      "is_active": true,
      "created_at": "2026-01-13T06:00:00.000Z",
      "expires_at": "2026-02-12T06:00:00.000Z",
      "customer_email": "john@example.com",
      "customer_name": "John Doe",
      "company": "Acme Inc"
    }
  ]
}
```

**Status Codes:**
- `200` - Success

---

## 🔐 Admin Endpoints

### 7. `POST /admin/reset-system`

**Reset entire system (clear all licenses)**

⚠️ **DANGEROUS**: This deletes all licenses from Redis and memory!

**Request:**
```bash
curl -X POST https://shadow-watch-three.vercel.app/admin/reset-system \
  -H "Content-Type: application/json" \
  -d '{
    "admin_secret": "shadow-watch-reset-2026"
  }'
```

**Request Body:**
```typescript
{
  admin_secret: string;  // Admin password
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "System reset successful. Cleared 142 licenses.",
  "note": "Supabase user data retained for analytics"
}
```

**Response (Unauthorized):**
```json
{
  "detail": "Unauthorized"
}
```

**Status Codes:**
- `200` - Success
- `403` - Unauthorized (wrong admin_secret)
- `500` - Server error

---

## 🔌 Integration Examples

### JavaScript/TypeScript (Fetch)

```typescript
// Generate trial license
async function generateTrial(name: string, email: string) {
  const response = await fetch('https://shadow-watch-three.vercel.app/trial', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, company: 'My Startup' })
  });
  
  const data = await response.json();
  console.log('License Key:', data.license_key);
  return data;
}

// Verify license
async function verifyLicense(licenseKey: string) {
  const response = await fetch(`https://shadow-watch-three.vercel.app/verify/${licenseKey}`);
  const data = await response.json();
  
  if (data.valid) {
    console.log('Valid! Events used:', data.events_used, '/', data.max_events);
  } else {
    console.log('Invalid:', data.reason);
  }
  
  return data;
}

// Usage
const trial = await generateTrial('John Doe', 'john@example.com');
const verification = await verifyLicense(trial.license_key);
```

---

### Python (requests)

```python
import requests

# Generate trial license
def generate_trial(name: str, email: str, company: str = "Individual"):
    response = requests.post(
        'https://shadow-watch-three.vercel.app/trial',
        json={
            'name': name,
            'email': email,
            'company': company
        }
    )
    data = response.json()
    print(f"License Key: {data['license_key']}")
    return data

# Verify license
def verify_license(license_key: str):
    response = requests.get(
        f'https://shadow-watch-three.vercel.app/verify/{license_key}'
    )
    data = response.json()
    
    if data['valid']:
        print(f"Valid! Events: {data['events_used']}/{data['max_events']}")
    else:
        print(f"Invalid: {data['reason']}")
    
    return data

# Usage
trial = generate_trial("John Doe", "john@example.com")
verification = verify_license(trial['license_key'])
```

---

### cURL Examples

```bash
# Generate trial
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","company":"Acme Inc"}'

# Verify license
curl https://shadow-watch-three.vercel.app/verify/SW-TRIAL-A3F2C1B4E5D6F7A8

# Health check
curl https://shadow-watch-three.vercel.app/health

# Get stats
curl https://shadow-watch-three.vercel.app/stats

# List all licenses
curl https://shadow-watch-three.vercel.app/licenses

# Admin reset (dangerous!)
curl -X POST https://shadow-watch-three.vercel.app/admin/reset-system \
  -H "Content-Type: application/json" \
  -d '{"admin_secret":"shadow-watch-reset-2026"}'
```

---

## 💾 Storage Architecture

The license server uses **3-layer storage** for reliability:

### Layer 1: Redis (Primary)
- **Fast**: ~5ms lookups
- **Persistent**: Data survives restarts
- **Multi-instance**: Shared across Vercel deployments

### Layer 2: Supabase (Analytics)
- **PostgreSQL**: User data for analytics
- **Persistent**: Long-term storage
- **Query-able**: Dashboard analytics

### Layer 3: Memory (Fallback)
- **Instant**: ~1ms lookups
- **Volatile**: Resets on deployment
- **Always available**: No external dependencies

**Reliability:**
- If Redis fails → falls back to Memory
- If Supabase fails → still works (just no analytics)
- Data written to all available layers simultaneously

---

## 🎯 Usage Limits

### Trial Tier
- **Duration**: 30 days from creation
- **Event Limit**: 10,000 events
- **Features**: Full access
- **Cost**: FREE

### Enterprise Tier (Future)
- **Duration**: 1 year
- **Event Limit**: Unlimited
- **Features**: Full access + priority support
- **Cost**: Contact sales

---

## 🔒 Security

### CORS Policy
The server accepts requests from:
- `https://shadow-watch-client.vercel.app` (Production)
- `https://shadow-watch-client.onrender.com` (Alt deployment)
- `http://localhost:5173` (Vite dev)
- `http://localhost:3000` (React dev)
- `*` (Wildcard for testing - will be restricted in production)

### Rate Limiting
Currently **no rate limiting** (will add 100 req/min per IP in production)

### Admin Endpoints
Protected by `admin_secret`. Change this in production!

---

## 📊 Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | License verified, trial generated |
| 403 | Forbidden | Wrong admin secret |
| 404 | Not Found | Invalid endpoint |
| 422 | Validation Error | Missing required field |
| 500 | Server Error | Redis/Supabase down |

---

## 🚀 Quick Start

1. **Generate trial key:**
```bash
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{"name":"Your Name","email":"you@example.com"}'
```

2. **Copy the `license_key` from response**

3. **Use in your Python code:**
```python
from shadowwatch import ShadowWatch

sw = ShadowWatch(
    database_url="sqlite+aiosqlite:///./shadowwatch.db",
    license_key="SW-TRIAL-YOUR-KEY-HERE"  # Paste your key
)
```

4. **That's it!** Shadow Watch will automatically verify your license on first use.

---

## 📞 Support

- **Docs**: https://shadow-watch-client.vercel.app
- **Issues**: https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email**: tanishqdasari2004@gmail.com

---

**Last Updated**: Jan 13, 2026
