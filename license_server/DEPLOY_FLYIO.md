# Deploying Shadow Watch License Server to Fly.io

## Prerequisites

### 1. Install Fly CLI

**Windows CMD (Command Prompt):**
```cmd
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```
After installation, **close and reopen CMD** for the PATH to update.

**Windows PowerShell:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Linux/macOS:**
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Create Fly.io Account
- Go to https://fly.io/app/sign-up
- Sign up with GitHub (easiest)

### 3. How Deployment Works
Fly.io auto-detects Python apps by finding:
- `requirements.txt` (in repository root)
- `Procfile` (in license_server directory)

**No Docker needed!** Fly.io looks in the root directory for requirements.txt automatically.

---

## Quick Deployment (5 Minutes)

### Option 1: Automated Script (Recommended)

**Windows CMD:**
```cmd
cd license_server
deploy.bat
```

**Windows PowerShell:**
```powershell
cd license_server
.\deploy.bat
```

**Linux/macOS:**
```bash
cd license_server
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Step-by-Step

**Windows CMD/PowerShell:**
```cmd
cd license_server
flyctl auth login
flyctl launch --name shadowwatch-license --region ord --no-deploy
flyctl volumes create license_data --size 1 --region ord
flyctl deploy
flyctl info
```

**Linux/macOS:**

```bash
# 1. Navigate to license server
cd license_server

# 2. Login to Fly.io
flyctl auth login

# 3. Initialize app
flyctl launch --name shadowwatch-license --region ord --no-deploy

# 4. Create persistent volume (for SQLite)
flyctl volumes create license_data --size 1 --region ord

# 5. Deploy
flyctl deploy

# 6. Get your URL
flyctl info
```

---

## Post-Deployment

### 1. Generate Trial Keys

**Windows CMD/PowerShell:**
```cmd
flyctl ssh console -C "python generate_trial_keys.py"
```

**Linux/macOS:**
```bash
flyctl ssh console -C 'python generate_trial_keys.py'
```

This will output 10 trial keys like:
```
✅ Generated: SW-TRIAL-A7B2-C3D4-E5F6-G7H8
✅ Generated: SW-TRIAL-I9J0-K1L2-M3N4-O5P6
...
```

### 2. Test Endpoints

**Health Check:**
```cmd
curl https://shadowwatch-license.fly.dev/
```

**Verify License (Windows CMD):**
```cmd
curl -X POST https://shadowwatch-license.fly.dev/verify -H "Content-Type: application/json" -d "{\"key\": \"SW-TRIAL-A7B2-C3D4-E5F6-G7H8\"}"
```

**Verify License (PowerShell):**
```powershell
curl -X POST https://shadowwatch-license.fly.dev/verify -H "Content-Type: application/json" -d '{"key": "SW-TRIAL-A7B2-C3D4-E5F6-G7H8"}'
```

**Get Stats:**
```cmd
curl https://shadowwatch-license.fly.dev/stats
```

### 3. Update Shadow Watch Library

Update `shadowwatch/utils/license.py`:

```python
# Change:
LICENSE_SERVER_URL = "https://license-shadowwatch.railway.app"

# To:
LICENSE_SERVER_URL = "https://shadowwatch-license.fly.dev"
```

---

## Monitoring

### View Logs
```bash
flyctl logs
```

### View Metrics
```bash
flyctl status
```

### SSH Into Container
```bash
flyctl ssh console
```

---

## Scaling (Future)

### Add More Regions
```bash
flyctl regions add lax sjc  # West coast
flyctl scale count 3  # 3 instances
```

### Upgrade Resources
```bash
flyctl scale vm shared-cpu-2x  # 2 CPUs
flyctl scale memory 512  # 512MB RAM
```

---

## Troubleshooting

### Issue: "App name already taken"

**Solution:**
```bash
flyctl launch --name shadowwatch-license-yourname --region ord --no-deploy
```

### Issue: "Volume creation failed"

**Solution:** Choose a different region:
```bash
flyctl regions list  # See available regions
flyctl volumes create license_data --size 1 --region lax
```

### Issue: Database not persisting

**Check volume is mounted:**
```bash
flyctl ssh console
ls -la /data
```

Should show `licenses.db` file.

---

## Cost

**Free Tier:**
- 3 shared-cpu VMs
- 3GB RAM total
- 160GB outbound transfer/month
- **More than enough for MVP**

**If you exceed free tier:**
- ~$2-5/month for basic usage
- Pay-as-you-go

---

## Next Steps

1. ✅ Deploy license server to Fly.io
2. ✅ Generate 10 trial keys
3. ✅ Update Shadow Watch library with Fly.io URL
4. ✅ Test end-to-end (Shadow Watch → Fly.io → verification)
5. ✅ Commit changes to GitHub

---

**Your License Server URL:**
```
https://shadowwatch-license.fly.dev
```

Use this in your Shadow Watch initialization:
```python
sw = ShadowWatch(
    database_url="...",
    license_key="SW-TRIAL-XXXX-...",
    license_server_url="https://shadowwatch-license.fly.dev"
)
```

**Done!** 🎉
