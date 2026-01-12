from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import os
import json
import string
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Core Modules
from kv_store import LicenseStore
from database import SessionLocal, init_db, User, AuditLog

app = FastAPI(title="Shadow Watch License Server")

# ✅ FINAL CORS CONFIGURATION (User Requested)
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

class ResetRequest(BaseModel):
    admin_secret: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize DB on Startup
@app.on_event("startup")
async def startup():
    try:
        init_db()
        print("✅ Database Initialized")
    except Exception as e:
        print(f"❌ DB Init Error: {e}")

@app.get("/")
async def root():
    return {
        "service": "Shadow Watch License Server",
        "status": "operational",
        "version": "1.2.0",
        "storage": "Redis + CockroachDB"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    health = {"status": "operational", "database": "connected", "redis": "connected"}
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    if not LicenseStore._use_redis():
        health["redis"] = "using-memory-fallback"
    
    return health

@app.post("/trial")
async def create_trial_license(req: TrialRequest, db: Session = Depends(get_db)):
    """Generate a 30-day trial license key"""
    # 1. Check if user exists
    user = db.query(User).filter(User.email == req.email).first()
    
    if user:
        existing_trial = db.query(AuditLog).filter(
            AuditLog.actor_id == user.id,
            AuditLog.action == "license.created_trial"
        ).first()
        if existing_trial:
            raise HTTPException(status_code=400, detail="Trial already generated for this email.")

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
    
    # 3. Store in Redis
    expires_at = datetime.utcnow() + timedelta(days=30)
    license_data = {
        "key": key,
        "owner_id": user.id,
        "owner_email": user.email,
        "tier": "trial",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
    }
    
    LicenseStore.save_license(key, license_data)

    # 4. Audit Log
    db.add(AuditLog(
        action="license.created_trial",
        actor_id=user.id,
        target_id=key,
        details=f"Trial generated for {user.email}"
    ))
    db.commit()

    return {
        "success": True,
        "license_key": key,
        "expires_at": expires_at.isoformat(),
        "message": "30-day trial activated."
    }

@app.get("/verify/{license_key}")
async def verify_license(license_key: str):
    license = LicenseStore.get_license(license_key)
    if not license:
        return {"valid": False, "reason": "not_found"}
    
    expires_at = datetime.fromisoformat(license['expires_at'])
    if datetime.utcnow() > expires_at:
        return {"valid": False, "reason": "expired"}
    
    return {"valid": True, "tier": license.get("tier", "trial"), "expires_at": license['expires_at']}

@app.get("/stats")
async def get_stats():
    return LicenseStore.get_all_stats()

@app.post("/admin/reset-system")
async def reset_system(req: ResetRequest, db: Session = Depends(get_db)):
    if req.admin_secret != "shadow-watch-reset-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    try:
        from sqlalchemy import text
        db.execute(text("DELETE FROM audit_logs"))
        db.execute(text("DELETE FROM users WHERE password IS NULL"))
        db.commit()
        LicenseStore.clear_all()
        return {"success": True, "message": "Full system reset successful."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
