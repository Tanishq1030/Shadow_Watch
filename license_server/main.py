from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Import Redis-based store (works with Vercel KV or local Redis)
from kv_store import LicenseStore

app = FastAPI(title="Shadow Watch License Server")

# No database initialization needed (Redis/KV is managed externally)

# Request/Response models
class VerifyRequest(BaseModel):
    key: str

class ReportRequest(BaseModel):
    license_key: str
    events_count: int
    timestamp: str


@app.on_event("startup")
async def startup():
    """Startup message"""
    print("✅ Shadow Watch License Server started")
    print("💾 Storage: Redis/Vercel KV (serverless-compatible)")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Shadow Watch License Server",
        "status": "operational",
        "version": "1.0.0",
        "storage": "Redis/Vercel KV"
    }


@app.post("/admin/generate-keys")
async def admin_generate_keys(count: int = 10):
    """
    Admin endpoint: Generate trial license keys
    
    Usage:
        curl -X POST "https://your-server.com/admin/generate-keys?count=10"
    
    Args:
        count: Number of trial keys to generate (default: 10)
    
    Returns:
        JSON with generated keys and expiration date
    """
    import secrets
    import string
    from datetime import timedelta
    
    def generate_key():
        """Generate unique trial key"""
        chars = string.ascii_uppercase + string.digits
        parts = [
            ''.join(secrets.choice(chars) for _ in range(4))
            for _ in range(4)
        ]
        return f"SW-TRIAL-{'-'.join(parts)}"
    
    # Generate keys
    created_keys = []
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    for i in range(count):
        key = generate_key()
        
        success = LicenseStore.save_license(
            license_key=key,
            tier="trial",
            max_events=10000,
            customer_name=f"Trial User {i+1}",
            customer_email="",
            expires_at=expires_at
        )
        
        if success:
            created_keys.append(key)
    
    return {
        "success": True,
        "generated": len(created_keys),
        "expires_at": expires_at[:10],
        "max_events": 10000,
        "keys": created_keys
    }


from pydantic import EmailStr

class TrialRequest(BaseModel):
    name: str
    email: EmailStr
    company: str = "Individual"
    use_case: str = ""


@app.post("/trial")
async def create_trial_license(req: TrialRequest):
    """
    Self-service trial license generation
    
    Instantly generates a 30-day trial license (10,000 events).
    No manual approval required!
    
    Returns: {
        "success": true,
        "license_key": "SW-TRIAL-XXXX-XXXX-XXXX-XXXX",
        "expires_at": "2026-02-10T...",
        "max_events": 10000
    }
    """
    import secrets
    import string
    from datetime import timedelta
    
    def generate_trial_key():
        chars = string.ascii_uppercase + string.digits
        parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
        return f"SW-TRIAL-{'-'.join(parts)}"
    
    # Generate trial license
    license_key = generate_trial_key()
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    # Save to Redis/KV
    LicenseStore.save_license(
        license_key=license_key,
        tier="trial",
        max_events=10000,
        customer_name=req.name,
        customer_email=req.email,
        expires_at=expires_at
    )
    
    return {
        "success": True,
        "license_key": license_key,
        "expires_at": expires_at,
        "max_events": 10000,
        "message": "Trial license created! Valid for 30 days."
    }

@app.post("/verify")
async def verify_license(req: VerifyRequest):
    """
    Verify if license key is valid and not expired
    
    Returns license details if valid, 403 if invalid/expired
    """
    # Get from Redis/KV
    license_data = LicenseStore.get_license(req.key)
    
    if not license_data:
        raise HTTPException(status_code=403, detail="License key not found")
    
    # Check if expired
    try:
        expires_at = datetime.fromisoformat(license_data["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(status_code=403, detail="License key expired")
    except (KeyError, ValueError):
        raise HTTPException(status_code=403, detail="Invalid license data")
    
    # Check if active
    if not license_data.get("is_active", True):
        raise HTTPException(status_code=403, detail="License key deactivated")
    
    return {
        "valid": True,
        "tier": license_data["tier"],
        "max_events": license_data["max_events"],
        "customer": license_data.get("customer_name", "Trial User"),
        "expires_at": license_data["expires_at"]
    }


@app.post("/report")
async def report_usage(req: ReportRequest):
    """
    Receive usage report from customer's Shadow Watch instance
    
    Stores event count for billing/monitoring
    """
    # Verify license exists
    license_data = LicenseStore.get_license(req.license_key)
    if not license_data:
        raise HTTPException(status_code=404, detail="License key not found")
    
    # Store usage report
    LicenseStore.report_usage(
        req.license_key,
        req.events_count,
        req.timestamp
    )
    
    return {"status": "received"}


@app.get("/stats")
async def get_stats():
    """
    Admin endpoint: Get usage statistics
    
    Returns total customers, licenses, and events
    """
    licenses = LicenseStore.list_all_licenses()
    
    # Count active licenses
    active_licenses = [l for l in licenses if l.get("is_active", True)]
    
    # Count active trials (not expired)
    active_trials = [
        l for l in active_licenses 
        if l.get("tier") == "trial" and 
        datetime.fromisoformat(l["expires_at"]) > datetime.utcnow()
    ]
    
    # Total events tracked
    total_events = sum(
        LicenseStore.get_total_events(l["license_key"]) 
        for l in licenses
    )
    
    return {
        "total_licenses": len(active_licenses),
        "active_trials": len(active_trials),
        "total_events_tracked": total_events
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
