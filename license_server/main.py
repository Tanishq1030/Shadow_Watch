from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import os
import json
import string
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# Core Modules
from database import SessionLocal, init_db, User, License, AuditLog

app = FastAPI(title="Shadow Watch License Server")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shadow-watch-client.onrender.com",
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
        "version": "2.0.0",
        "storage": "CockroachDB (PostgreSQL)"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    health = {"status": "operational", "database": "connected"}
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    return health

@app.post("/trial")
async def create_trial_license(req: TrialRequest, db: Session = Depends(get_db)):
    """Generate a 30-day trial license key"""
    # 1. Check if user exists
    user = db.query(User).filter(User.email == req.email).first()
    
    if user:
        # Check if trial already generated
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

    # 2. Generate license key
    key = f"SW-TRIAL-{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))}"
    
    # 3. Store in database
    expires_at = datetime.utcnow() + timedelta(days=30)
    license = License(
        key=key,
        owner_id=user.id,
        owner_email=user.email,
        tier="trial",
        is_active=True,
        expires_at=expires_at,
        metadata=json.dumps({"org": req.company})
    )
    db.add(license)

    # 4. Audit Log
    db.add(AuditLog(
        action="license.created_trial",
        actor_id=user.id,
        target_id=key,
        details=f"Trial generated for {user.email}",
        ip_address="0.0.0.0"
    ))
    db.commit()

    return {
        "success": True,
        "license_key": key,
        "expires_at": expires_at.isoformat(),
        "message": "30-day trial activated."
    }

@app.get("/verify/{license_key}")
async def verify_license(license_key: str, db: Session = Depends(get_db)):
    """Verify if a license key is valid"""
    license = db.query(License).filter(License.key == license_key).first()
    
    if not license:
        return {"valid": False, "reason": "not_found"}
    
    if datetime.utcnow() > license.expires_at:
        return {"valid": False, "reason": "expired"}
    
    if not license.is_active:
        return {"valid": False, "reason": "revoked"}
    
    return {
        "valid": True,
        "tier": license.tier,
        "expires_at": license.expires_at.isoformat()
    }

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get license statistics"""
    active_licenses = db.query(License).filter(
        License.is_active == True,
        License.expires_at > datetime.utcnow()
    ).count()
    
    active_trials = db.query(License).filter(
        License.is_active == True,
        License.tier == "trial",
        License.expires_at > datetime.utcnow()
    ).count()
    
    return {
        "active_licenses": active_licenses,
        "active_trials": active_trials,
        "total_events": 0  # Can add usage tracking later
    }

@app.post("/admin/reset-system")
async def reset_system(req: ResetRequest, db: Session = Depends(get_db)):
    """Reset the entire system (admin only)"""
    if req.admin_secret != "shadow-watch-reset-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # Delete all licenses, trial users, and audit logs
        db.query(License).delete()
        db.query(AuditLog).delete()
        db.query(User).filter(User.password == None).delete()
        db.commit()
        return {"success": True, "message": "Full system reset successful."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
