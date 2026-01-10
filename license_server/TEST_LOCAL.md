# Test License Server Locally

## Quick Test Commands

1. **Install dependencies:**
```bash
cd d:\Shadow_Watch
pip install -r requirements.txt
```

2. **Start the server:**
```bash
cd d:\Shadow_Watch\license_server
python main.py
```

2. **Generate trial keys:**
```bash
# In another terminal
cd d:\Shadow_Watch\license_server
python generate_trial_keys.py
```

3. **Test health check:**
```bash
curl http://localhost:8000/
```

4. **Test license verification:**
```bash
# Replace SW-TRIAL-XXXX-... with actual key from generate_trial_keys.py
curl -X POST http://localhost:8000/verify -H "Content-Type: application/json" -d "{\"key\": \"SW-TRIAL-XXXX-XXXX-XXXX-XXXX\"}"
```

5. **Check stats:**
```bash
curl http://localhost:8000/stats
```

## Expected Results

✅ Health check returns: `{"service": "Shadow Watch License Server", "status": "operational"}`
✅ License verification returns: `{"valid": true, "tier": "trial", ...}`
✅ Stats shows: `{"total_licenses": 10, "active_trials": 10, ...}`

## Next Step: Railway Deployment

Once local testing passes, deploy to Railway.app
