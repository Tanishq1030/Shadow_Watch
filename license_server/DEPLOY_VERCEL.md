# Shadow Watch License Server - Vercel Deployment Guide

## Prerequisites

1. **Vercel Account** (No credit card required!)
   - Go to: https://vercel.com/signup
   - Sign up with GitHub (easiest)
   
2. **Vercel CLI** (Optional - can use web interface)
   ```cmd
   npm install -g vercel
   ```

---

## Deployment Methods

### Method 1: Vercel CLI (Recommended - Fastest)

**Step 1: Install dependencies locally**
```cmd
cd d:\Shadow_Watch
pip install -r requirements.txt
```

**Step 2: Login to Vercel**
```cmd
vercel login
# Opens browser → Authorize
```

**Step 3: Deploy**
```cmd
cd license_server
vercel

# Follow prompts:
# - Set up and deploy? Y
# - Which scope? (your account)
# - Link to existing project? N
# - What's your project's name? shadowwatch-license
# - In which directory is your code? ./
# - Want to override settings? N
```

**You'll get:** `https://shadowwatch-license.vercel.app`

**Step 4: Set up Vercel KV (Redis)**

Via Web Dashboard:
1. Go to https://vercel.com/dashboard
2. Select `shadowwatch-license` project
3. **Storage** tab → **Create Database** → **KV**
4. Name: `shadowwatch-kv`
5. Click **Create**
6. Environment variables auto-added:
   - `KV_REST_API_URL`
   - `KV_REST_API_TOKEN`

**Step 5: Redeploy (to activate KV)**
```cmd
vercel --prod
```

**Step 6: Generate Trial Keys**

Option A - Use Vercel CLI:
```cmd
# Pull env vars locally
vercel env pull .env.local

# Generate keys (connects to Vercel KV)
python generate_trial_keys.py
```

Option B - SSH to Vercel (if available):
```cmd
vercel run python generate_trial_keys.py
```

---

### Method 2: GitHub Integration (Easiest - Auto-deploy)

**Step 1: Push to GitHub**
```cmd
cd d:\Shadow_Watch
git add .
git commit -m "Refactored license server for Vercel"
git push origin main
```

**Step 2: Connect Vercel to GitHub**
1. Go to: https://vercel.com/new
2. **Import Git Repository**
3. Select `Tanishq1030/Shadow_Watch`
4. **Root Directory:** `license_server`
5. Click **Deploy**

**Step 3: Set up Vercel KV**
(Same as Method 1, Step 4)

**Step 4: Generate Keys**
```cmd
# Clone repo locally if needed
git clone https://github.com/Tanishq1030/Shadow_Watch
cd Shadow_Watch

# Pull Vercel env vars
cd license_server
vercel link  # Link to your Vercel project
vercel env pull .env.local

# Generate keys
python generate_trial_keys.py
```

---

## Testing

**Health Check:**
```cmd
curl https://shadowwatch-license.vercel.app/
```

**Expected:**
```json
{"service":"Shadow Watch License Server","status":"operational","version":"1.0.0","storage":"Redis/Vercel KV"}
```

**Verify License:**
```cmd
curl -X POST https://shadowwatch-license.vercel.app/verify -H "Content-Type: application/json" -d "{\"key\": \"SW-TRIAL-XXXX-XXXX-XXXX-XXXX\"}"
```

**Expected:**
```json
{"valid":true,"tier":"trial","max_events":10000,"customer":"Trial User 1","expires_at":"2026-02-09T..."}
```

**Stats:**
```cmd
curl https://shadowwatch-license.vercel.app/stats
```

---

## Local Development (with In-Memory Fallback)

If you want to test without Redis:

```cmd
cd d:\Shadow_Watch\license_server

# Run server (uses in-memory storage)
python main.py

# Generate keys (in-memory)
python generate_trial_keys.py

# Test
curl http://localhost:8000/
```

**Note:** In-memory storage = data lost when server restarts. Only for testing!

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'kv_store'"

**Fix:**
```cmd
# Make sure you're in license_server directory
cd d:\Shadow_Watch\license_server

# Verify kv_store.py exists
dir kv_store.py
```

### Issue: "Redis connection failed"

**Expected!** Locally, it falls back to in-memory storage.

For production, Vercel KV will be automatically configured.

### Issue: "vercel command not found"

**Fix:**
```cmd
# Install Vercel CLI
npm install -g vercel

# Or use npx (no install)
npx vercel
```

---

## Environment Variables (Vercel)

Vercel KV automatically sets:
- `KV_REST_API_URL` - Redis connection URL
- `KV_REST_API_TOKEN` - Authentication token

These are injected at runtime, no manual configuration needed!

---

## Next Steps

After deployment:

1. ✅ Test all endpoints
2. ✅ Generate 10 trial keys
3. ✅ Update `shadowwatch/utils/license.py`:
   ```python
   LICENSE_SERVER_URL = "https://shadowwatch-license.vercel.app"
   ```
4. ✅ Test Shadow Watch library integration
5. ✅ Commit and push

---

## Free Tier Limits

Vercel Free Tier:
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Serverless functions (1000 hours/month)
- ✅ **No credit card required**

Vercel KV (Redis):
- ✅ 256 MB storage
- ✅ 3,000 commands/day
- ✅ **Perfect for license server**

---

Your license server is now serverless-compatible! 🎉
