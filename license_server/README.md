# Shadow Watch License Server

Standalone FastAPI server for managing Shadow Watch license keys and usage tracking.

## Local Development

```bash
# Install dependencies (from root)
pip install -r ../requirements.txt

# Run server
python main.py

# Server runs on http://localhost:8000
```

## Generate Trial Keys

```bash
# Generate 10 trial keys (30-day expiration)
python generate_trial_keys.py
```

## API Endpoints

### GET /
Health check endpoint

### POST /verify
Verify license key validity

Request:
```json
{
  "key": "SW-TRIAL-XXXX-XXXX-XXXX-XXXX"
}
```

Response (valid):
```json
{
  "valid": true,
  "tier": "trial",
  "max_events": 10000,
  "customer": "Trial User 1",
  "expires_at": "2026-02-10T..."
}
```

### POST /report
Report usage statistics

Request:
```json
{
  "license_key": "SW-TRIAL-XXXX-XXXX-XXXX-XXXX",
  "events_count": 1523,
  "timestamp": "2026-01-10T12:00:00Z"
}
```

### GET /stats
Admin statistics (total licenses, events, trials)

## Deployment (Fly.io)

See [DEPLOY_FLYIO.md](./DEPLOY_FLYIO.md) for complete deployment guide.

**Quick start:**

**Windows CMD:**
```cmd
deploy.bat
```

**Linux/macOS:**
```bash
chmod +x deploy.sh && ./deploy.sh
```

**Manual (all platforms):**
```cmd
flyctl auth login
flyctl launch --name shadowwatch-license --no-deploy
flyctl volumes create license_data --size 1
flyctl deploy
```

**Your URL:** `https://shadowwatch-license.fly.dev`

## Database

SQLite database (`licenses.db`) with 2 tables:
- `licenses` - License keys and metadata
- `usage_reports` - Event count reports from customers

## Environment Variables

None required for local development. Railway deployment uses default SQLite.
