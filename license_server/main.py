from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import os
import json
import string
from fastapi.middleware.cors import CORSMiddleware

# Defensive imports to prevent Vercel boot crashes
try:
    from sqlalchemy.orm import Session
    from kv_store import LicenseStore
    from database import SessionLocal, init_db, User, AuditLog
except Exception as e:
    print(f"📡 Import Warning: {e}")
    LicenseStore = None
    SessionLocal = None
    init_db = None
    User = None
    AuditLog = None

app = FastAPI(title="Shadow Watch License Server")

# Refined CORS Configuration (User Requested)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shadow-watch-client.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class TrialRequest(BaseModel):
    name: str
    email: str
    company: str = "Individual"

class VerifyRequest(BaseModel):
    key: str

class ReportRequest(BaseModel):
    license_key: str
    events_count: int
    timestamp: str

class ResetRequest(BaseModel):
    admin_secret: str

# Dependency
def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="Database module failed to load")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    print("🚀 Shadow Watch License Server v1.1.1 Starting...")
    print(f"📡 DB URL Present: {bool(os.getenv('DATABASE_URL'))}")

# Initialize DB
# Moved out of global scope to prevent server crashes if DB is unreachable
@app.get("/")
async def root():
    return {
        "service": "Shadow Watch License Server",
        "status": "operational",
        "version": "1.1.1",
        "storage": "Redis + MySQL"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db_url = os.getenv("DATABASE_URL") or ""
    health = {
        "status": "checking",
        "database": "unknown",
        "redis": "unknown",
        "env": {
            "has_db_url": bool(db_url),
            "db_protocol": db_url.split(":")[0] if ":" in db_url else "none",
            "db_host_len": len(db_url.split("@")[-1].split("/")[0]) if "@" in db_url else 0,
            "has_redis_url": bool(os.getenv("REDIS_URL") or os.getenv("KV_REST_API_URL")),
        }
    }
    
    # Check DB
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health["database"] = "connected"
    except Exception as e:
        health["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        if LicenseStore and LicenseStore._use_redis():
            health["redis"] = "connected"
        else:
            health["redis"] = "using-memory-fallback" if LicenseStore else "module_missing"
    except Exception as e:
        health["redis"] = f"error: {str(e)}"
        
    health["status"] = "operational" if health["database"] == "connected" else "degraded"
    return health

@app.post("/trial")
async def create_trial_license(req: TrialRequest, db: Session = Depends(get_db)):
    """Generate a 30-day trial license key"""
    if not LicenseStore:
        raise HTTPException(status_code=500, detail="Storage module not loaded")

    # 1. Check if user exists, else create guest
    user = db.query(User).filter(User.email == req.email).first()
    
    if user:
        existing_trial = db.query(AuditLog).filter(
            AuditLog.actor_id == user.id,
            AuditLog.action == "license.created_trial"
        ).first()
        if existing_trial:
            raise HTTPException(
                status_code=400, 
                detail="A trial license has already been generated for this email."
            )

    if not user:
        user = User(
            id=secrets.token_hex(16),
            email=req.email,
            name=req.name,
            company=req.company,
            password=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Generate key
    key = f"SW-TRIAL-{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))}"
    
    # 3. Store in Hot Storage (Redis)
    expires_at = datetime.utcnow() + timedelta(days=30)
    license_data = {
        "key": key,
        "owner_id": user.id,
        "owner_email": user.email,
        "tier": "trial",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
        "metadata": {"org": req.company}
    }
    
    success = LicenseStore.save_license(key, license_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save license to hot storage")

    # 4. Audit Log
    log = AuditLog(
        action="license.created_trial",
        actor_id=user.id,
        target_id=key,
        details=f"Trial generated for {user.email}",
        ip_address="0.0.0.0" # Placeholder
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "license_key": key,
        "expires_at": expires_at.isoformat(),
        "message": "30-day trial activated successfully."
    }

@app.get("/verify/{license_key}")
async def verify_license(license_key: str):
    if not LicenseStore:
        raise HTTPException(status_code=500, detail="Storage module not loaded")
    
    license = LicenseStore.get_license(license_key)
    if not license:
        return {"valid": False, "reason": "not_found"}
    
    # Check expiry
    expires_at = datetime.fromisoformat(license['expires_at'])
    if datetime.utcnow() > expires_at:
        return {"valid": False, "reason": "expired"}
    
    if not license.get("is_active", True):
        return {"valid": False, "reason": "revoked"}
        
    return {
        "valid": True,
        "tier": license.get("tier", "trial"),
        "expires_at": license['expires_at']
    }

@app.get("/stats")
async def get_stats():
    if not LicenseStore:
        return {"active_licenses": 0, "active_trials": 0, "total_events": 0}
    return LicenseStore.get_all_stats()

@app.post("/admin/reset-redis")
async def reset_redis(req: ResetRequest):
    if req.admin_secret != "shadow-watch-reset-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    if LicenseStore and LicenseStore.clear_all():
        return {"success": True, "message": "Redis cache cleared."}
    raise HTTPException(status_code=500, detail="Failed to clear Redis.")

@app.post("/admin/reset-system")
async def reset_system(req: ResetRequest, db: Session = Depends(get_db)):
    if req.admin_secret != "shadow-watch-reset-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    try:
        from sqlalchemy import text
        db.execute(text("DELETE FROM audit_logs WHERE action LIKE 'license.created_trial%'"))
        db.execute(text("DELETE FROM users WHERE password IS NULL"))
        db.commit()
        return {"success": True, "message": "Database reset successful."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB Reset failed: {str(e)}")
