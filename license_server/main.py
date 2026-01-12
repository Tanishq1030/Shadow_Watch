from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import secrets
import string
from datetime import timedelta
from sqlalchemy.orm import Session

# Import Redis-based store (works with Vercel KV or local Redis)
from kv_store import LicenseStore

# Import PlanetScale DB
from database import SessionLocal, init_db, User, AuditLog, Payment

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Shadow Watch License Server")

# Refined CORS Configuration
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

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize DB (create tables if needed - good for serverless cold starts)
try:
    init_db()
except Exception as e:
    print(f"⚠️ DB Init Warning: {e}")

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
    print("💾 Storage: Redis (Hot) + PlanetScale MySQL (Cold)")


@app.on_event("startup")
async def startup_event():
    print("🚀 Shadow Watch License Server v1.0.6 Starting...")
    print(f"📡 DB URL Present: {bool(os.getenv('DATABASE_URL'))}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Shadow Watch License Server",
        "status": "operational",
        "version": "1.0.6",
        "storage": "Redis + MySQL"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Diagnostic endpoint to check DB and Redis health"""
    health = {
        "status": "checking",
        "database": "unknown",
        "redis": "unknown",
        "env": {
            "has_db_url": bool(os.getenv("DATABASE_URL")),
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
        if LicenseStore._use_redis():
            health["redis"] = "connected"
        else:
            health["redis"] = "using-memory-fallback"
    except Exception as e:
        health["redis"] = f"error: {str(e)}"
        
    health["status"] = "operational" if health["database"] == "connected" and "error" not in health["redis"] else "degraded"
    return health


@app.post("/admin/generate-keys")
async def admin_generate_keys(count: int = 10, db: Session = Depends(get_db)):
    """
    Admin endpoint: Generate trial license keys
    """
    
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
        
        # Save to Redis
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
            # Log to MySQL
            log = AuditLog(
                action="license.created_batch",
                target_id=key,
                actor_id="admin",
                details=f"Batch generation ({i+1}/{count})"
            )
            db.add(log)
    
    db.commit()
    
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

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    organization: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResetRequest(BaseModel):
    admin_secret: str

@app.post("/auth/register")
async def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user in CockroachDB"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        id=secrets.token_hex(16),
        email=req.email,
        name=req.name,
        company=req.organization,
        password=req.password # NOTE: Plaintext for now. In production, use bcrypt/argon2 hashing!
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "user": {
            "name": user.name,
            "email": user.email,
            "organization": user.company
        }
    }

@app.post("/auth/login")
async def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user against CockroachDB"""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.password != req.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "success": True,
        "user": {
            "name": user.name,
            "email": user.email,
            "organization": user.company
        }
    }

@app.post("/admin/reset-system")
async def reset_system(req: ResetRequest, db: Session = Depends(get_db)):
    """
    FACTORY RESET: Purge all trial keys, logs, and guest users.
    Use with CAUTION.
    """
    # Simple protection
    if req.admin_secret != "shadow-watch-reset-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        from sqlalchemy import text
        # Purge trial logs
        db.execute(text("DELETE FROM audit_logs WHERE action LIKE 'license.created_trial%'"))
        # Purge guest users
        db.execute(text("DELETE FROM users WHERE password IS NULL"))
        db.commit()
        
        return {
            "success": True,
            "message": "Database reset successful. Logs and guest users purged."
        }
    except Exception as e:
        db.rollback()
        # Log the full error to help debug connection issues
        print(f"❌ DB Reset Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DB Reset failed: {str(e)}")

@app.post("/admin/reset-redis")
async def reset_redis(req: ResetRequest):
    """
    Purge all hot storage (Redis/KV). This resets the dashboard stats.
    """
    if req.admin_secret != "shadow-watch-reset-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    success = LicenseStore.clear_all()
    if success:
        return {"success": True, "message": "Redis cache cleared. Stats reset to 0."}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear Redis.")


@app.post("/trial")
async def create_trial_license(req: TrialRequest, db: Session = Depends(get_db)):
    """
    Trial license generation (now allows auto-creation of guest users)
    """
    
    def generate_trial_key():
        chars = string.ascii_uppercase + string.digits
        parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
        return f"SW-TRIAL-{'-'.join(parts)}"
    
    # 1. Check if user exists, else create guest
    user = db.query(User).filter(User.email == req.email).first()
    
    # Check if this user already has a trial license
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
            password=None  # Guest user - no password
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Generate license key
    license_key = generate_trial_key()
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    # 3. Save to Redis/KV (Hot Storage)
    LicenseStore.save_license(
        license_key=license_key,
        tier="trial",
        max_events=10000,
        customer_name=req.name,
        customer_email=req.email,
        expires_at=expires_at
    )
    
    # 4. Log to MySQL (Audit Trail)
    log = AuditLog(
        action="license.created_trial",
        actor_id=user.id,
        target_id=license_key,
        details=f"Self-service trial for {req.email}",
        ip_address="0.0.0.0" # Placeholder, implies need for request object to get real IP
    )
    db.add(log)
    db.commit()
    
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
    (Reads only from Redis for speed)
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
    """
    # Verify license exists
    license_data = LicenseStore.get_license(req.license_key)
    if not license_data:
        raise HTTPException(status_code=404, detail="License key not found")
    
    # Store usage report in Redis (could eventually sync specific milestones to MySQL)
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
