# Shadow Watch Tests

This directory contains test files for Shadow Watch.

## Test Files

### `test_local_dev.py`
Tests Shadow Watch in **local development mode** (no license required).

**Features:**
- No license key needed
- 1,000 event limit
- Perfect for testing locally
- CI/CD pipelines

**Run:**
```bash
cd tests
python test_local_dev.py
```

**Expected output:**
```
⚠️  Shadow Watch: LOCAL DEV MODE (No License Required)
======================================================================
   • Limited to 1,000 events
   • For production, get free trial:
      https://shadow-watch-three.vercel.app/trial
======================================================================

✅ All tests pass
Events used: 15 / 1000
```

---

### `test_production.py`
Tests Shadow Watch with a **production/trial license** (unlimited events).

**Features:**
- Requires valid license key
- Unlimited events
- Full feature testing
- Multi-user support

**Get License:**
```bash
# Option 1: Instant trial (free, 30 days, 10k events)
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{"name":"Your Name","email":"your@email.com"}'

# Option 2: Email for production license
# Email: tanishqdasari2004@gmail.com
```

**Run:**
```bash
cd tests

# Set license key
set SHADOWWATCH_LICENSE_KEY=SW-TRIAL-XXXX-XXXX-XXXX-XXXX

# Run test
python test_production.py
```

**Expected output:**
```
✅ Shadow Watch: Licensed to John Doe (trial)

✅ All production tests pass
   • Activity tracking ✓
   • User profiling ✓
   • Login verification ✓
   • Library management ✓
```

---

## Quick Start

**1. Test Local Mode (No Setup):**
```bash
python test_local_dev.py
```

**2. Test Production Mode:**
```bash
# Get trial license
curl -X POST https://shadow-watch-three.vercel.app/trial \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}'

# Copy license key from response
set SHADOWWATCH_LICENSE_KEY=SW-TRIAL-your-key-here

# Run test
python test_production.py
```

---

## What's Tested

| Feature | Local Dev | Production |
|---------|-----------|------------|
| Activity Tracking | ✅ (1k limit) | ✅ (unlimited) |
| User Profiling | ✅ | ✅ |
| Login Verification | ✅ | ✅ |
| Library Management | ✅ | ✅ |
| License Verification | ⏭️ Skipped | ✅ Required |
| Multi-User Support | ✅ | ✅ |
| Event Limits | ✅ 1,000 | ❌ None |

---

## Troubleshooting

**Q: "No module named 'shadowwatch'"**
```bash
pip install shadowwatch
```

**Q: "No module named 'aiosqlite'"**
```bash
pip install aiosqlite
```

**Q: "License verification failed"**
- Check internet connection
- Verify license key is correct
- Check license hasn't expired
- Ensure firewall allows HTTPS to Vercel

**Q: "Local dev limit reached"**
- This is expected after 1,000 events
- Get trial license for unlimited events
- Or delete `test_local_dev.db` to reset

---

## CI/CD Integration

**Use local mode for testing in CI:**
```yaml
# .github/workflows/test.yml
- name: Test Shadow Watch
  run: |
    pip install shadowwatch aiosqlite
    python tests/test_local_dev.py
```

No license key needed for CI! ✅

---

## Need Help?

- **GitHub Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com
- **Docs:** https://github.com/Tanishq1030/Shadow_Watch
