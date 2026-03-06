# Shadow Watch Tests

This directory contains test files for Shadow Watch.

## Test Files

### `test_local_dev.py`

Tests Shadow Watch in **local development mode** (no license required, no Redis).

**Features:**

- No license key needed
- No event limits
- Perfect for testing locally
- CI/CD friendly

**Run:**

```bash
python tests/test_local_dev.py
```

---

### `test_production.py`

Tests Shadow Watch against a real PostgreSQL database.

**Features:**

- Full feature testing
- Multi-user support
- Unlimited events

**Run:**

```bash
# Set your database URL
set DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb

# Run test
python tests/test_production.py
```

---

### `test_day1_refactoring.py`

Verifies all features (including `calculate_continuity`) are freely available.

### `test_continuity.py`

Tests the behavioral continuity / ATO detection algorithm end-to-end.

### `test_simple.py`

Quick sanity check — initialize, track, get profile.

---

## Quick Start

**1. Set up your database:**

```bash
# Using PostgreSQL locally
createdb shadowwatch_test
```

**2. Run the test suite:**

```bash
pytest tests/
```

No license key required! ✅

---

## What's Tested

| Feature                   | Status              |
| ------------------------- | ------------------- |
| Activity Tracking         | ✅                  |
| User Profiling            | ✅                  |
| Login Verification        | ✅                  |
| Library Management        | ✅                  |
| Temporal Continuity (ATO) | ✅                  |
| Multi-User Support        | ✅                  |
| Event Limits              | ❌ None (unlimited) |

---

## CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Test Shadow Watch
  env:
    DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/shadowwatch_test
  run: |
    pip install shadowwatch
    pytest tests/
```

---

## Need Help?

- **GitHub Issues:** https://github.com/Tanishq1030/Shadow_Watch/issues
- **Email:** tanishqdasari2004@gmail.com
- **Docs:** https://github.com/Tanishq1030/Shadow_Watch
