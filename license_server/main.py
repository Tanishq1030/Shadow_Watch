from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import secrets
import json
import os

# Redis for primary storage
try:
    import redis
    redis_client = redis.from_url(
        os.getenv("REDIS_URL", ""),
        decode_responses=True
    )
    REDIS_AVAILABLE = True
    print("✅ Redis connected")
except Exception as e:
    print(f"⚠️ Redis not available: {e}")
    REDIS_AVAILABLE = False
    redis_client = None

# Supabase for backup (optional)
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        SUPABASE_AVAILABLE = True
        print("✅ Supabase connected")
    else:
        SUPABASE_AVAILABLE = False
        print("⚠️ Supabase credentials not found")
except Exception as e:
    print(f"⚠️ Supabase not available: {e}")
    SUPABASE_AVAILABLE = False
    supabase = None

# In-memory fallback (always available)
licenses_memory = {}

app = FastAPI(title="Shadow Watch License Server")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shadow-watch-client.onrender.com",
        "https://shadow-watch-client.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "*"  # Allow all for testing
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

# Helper Functions
def store_license(license_key: str, license_data: dict) -> dict:
    """Store license in all available storage layers"""
    storage_results = {
        "redis": False,
        "supabase": False,
        "memory": False
    }
    
    # 1. Store in Redis (primary)
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.set(
                f"license:{license_key}",
                json.dumps(license_data),
                ex=None  # No expiry - permanent
            )
            storage_results["redis"] = True
            print(f"✅ Stored in Redis: {license_key}")
        except Exception as e:
            print(f"⚠️ Redis storage failed: {e}")
    
    # 2. Store in Memory (always works)
    try:
        licenses_memory[license_key] = license_data
        storage_results["memory"] = True
        print(f"✅ Stored in Memory: {license_key}")
    except Exception as e:
        print(f"⚠️ Memory storage failed: {e}")
    
    return storage_results

def store_user_in_supabase(email: str, name: str, company: str) -> bool:
    """Store user in Supabase for analytics"""
    if not SUPABASE_AVAILABLE or not supabase:
        return False
    
    try:
        # Upsert user (insert or update if exists)
        result = supabase.table("users").upsert({
            "email": email,
            "name": name,
            "company": company
        }, on_conflict="email").execute()
        
        print(f"✅ User saved to Supabase: {email}")
        return True
    except Exception as e:
        print(f"⚠️ Supabase user storage failed: {e}")
        return False

def get_license(license_key: str) -> Optional[dict]:
    """Retrieve license from any available storage"""
    
    # Try Redis first (fastest)
    if REDIS_AVAILABLE and redis_client:
        try:
            data = redis_client.get(f"license:{license_key}")
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"⚠️ Redis lookup failed: {e}")
    
    # Try memory fallback
    if license_key in licenses_memory:
        return licenses_memory[license_key]
    
    return None

# API Endpoints
@app.get("/")
async def root():
    """Health check and service info"""
    return {
        "service": "Shadow Watch License Server",
        "status": "operational",
        "version": "2.1.0",
        "storage": {
            "redis": REDIS_AVAILABLE,
            "supabase": SUPABASE_AVAILABLE,
            "memory": True
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health = {
        "status": "operational",
        "storage": {
            "redis": "connected" if REDIS_AVAILABLE else "unavailable",
            "supabase": "connected" if SUPABASE_AVAILABLE else "unavailable",
            "memory": "connected"
        }
    }
    
    # Test Redis connection
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.ping()
            health["storage"]["redis"] = "connected"
        except Exception as e:
            health["storage"]["redis"] = f"error: {str(e)}"
    
    # Test Supabase connection
    if SUPABASE_AVAILABLE and supabase:
        try:
            # Simple query to test connection
            supabase.table("users").select("id").limit(1).execute()
            health["storage"]["supabase"] = "connected"
        except Exception as e:
            health["storage"]["supabase"] = f"error: {str(e)}"
    
    return health

@app.post("/trial")
async def create_trial_license(req: TrialRequest):
    """Generate a 30-day trial license key - GUARANTEED TO WORK"""
    
    try:
        # 1. Generate license key
        license_key = f"SW-TRIAL-{secrets.token_hex(8).upper()}"
        
        # 2. Create license data
        expires_at = datetime.utcnow() + timedelta(days=30)
        license_data = {
            "license_key": license_key,
            "tier": "trial",
            "max_events": 10000,
            "events_used": 0,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "customer_email": req.email,
            "customer_name": req.name,
            "company": req.company
        }
        
        # 3. Store license in available storage layers
        storage_results = store_license(license_key, license_data)
        
        # 4. Store user in Supabase (for analytics, non-blocking)
        supabase_saved = store_user_in_supabase(req.email, req.name, req.company)
        storage_results["supabase"] = supabase_saved
        
        # 5. Verify at least one storage succeeded
        if not any(storage_results.values()):
            raise HTTPException(
                status_code=500,
                detail="Failed to store license in any storage layer"
            )
        
        # 6. Return success
        return {
            "success": True,
            "license_key": license_key,
            "expires_at": expires_at.isoformat(),
            "max_events": 10000,
            "tier": "trial",
            "message": "30-day trial activated",
            "storage_used": storage_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Trial generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trial: {str(e)}"
        )

@app.get("/verify/{license_key}")
async def verify_license(license_key: str):
    """Verify if a license key is valid"""
    
    # Get license from storage
    license_data = get_license(license_key)
    
    if not license_data:
        return {"valid": False, "reason": "not_found"}
    
    # Check expiry
    try:
        expires_at = datetime.fromisoformat(license_data['expires_at'])
        if expires_at < datetime.utcnow():
            return {"valid": False, "reason": "expired"}
    except Exception as e:
        print(f"⚠️ Error parsing expiry date: {e}")
        return {"valid": False, "reason": "invalid_data"}
    
    # Check usage
    if license_data.get('events_used', 0) >= license_data.get('max_events', 10000):
        return {"valid": False, "reason": "limit_reached"}
    
    # Check active status
    if not license_data.get('is_active', True):
        return {"valid": False, "reason": "revoked"}
    
    return {
        "valid": True,
        "tier": license_data.get('tier', 'trial'),
        "events_used": license_data.get('events_used', 0),
        "max_events": license_data.get('max_events', 10000),
        "expires_at": license_data['expires_at']
    }

@app.get("/licenses")
async def list_licenses():
    """List all licenses (for admin dashboard)"""
    
    all_licenses = []
    
    # Get from Redis
    if REDIS_AVAILABLE and redis_client:
        try:
            keys = redis_client.keys("license:*")
            for key in keys:
                data = redis_client.get(key)
                if data:
                    all_licenses.append(json.loads(data))
            print(f"✅ Retrieved {len(all_licenses)} licenses from Redis")
        except Exception as e:
            print(f"⚠️ Redis list failed: {e}")
    
    # Add from memory (if Redis failed)
    if not all_licenses:
        all_licenses = list(licenses_memory.values())
        print(f"✅ Retrieved {len(all_licenses)} licenses from Memory")
    
    return {
        "total": len(all_licenses),
        "licenses": all_licenses
    }

@app.get("/stats")
async def get_stats():
    """Get license statistics"""
    
    total_licenses = 0
    active_licenses = 0
    expired_licenses = 0
    
    # Get from Redis or memory
    if REDIS_AVAILABLE and redis_client:
        try:
            keys = redis_client.keys("license:*")
            total_licenses = len(keys)
            
            for key in keys:
                data = redis_client.get(key)
                if data:
                    license_data = json.loads(data)
                    expires_at = datetime.fromisoformat(license_data['expires_at'])
                    
                    if license_data.get('is_active', True):
                        if expires_at > datetime.utcnow():
                            active_licenses += 1
                        else:
                            expired_licenses += 1
        except Exception as e:
            print(f"⚠️ Stats calculation failed: {e}")
    else:
        total_licenses = len(licenses_memory)
        for license_data in licenses_memory.values():
            expires_at = datetime.fromisoformat(license_data['expires_at'])
            if license_data.get('is_active', True):
                if expires_at > datetime.utcnow():
                    active_licenses += 1
                else:
                    expired_licenses += 1
    
    return {
        "total_licenses": total_licenses,
        "active_licenses": active_licenses,
        "expired_licenses": expired_licenses,
        "storage": {
            "redis": REDIS_AVAILABLE,
            "supabase": SUPABASE_AVAILABLE,
            "memory": True
        }
    }

@app.post("/admin/reset-system")
async def reset_system(req: ResetRequest):
    """Reset the entire system (admin only)"""
    
    if req.admin_secret != "shadow-watch-reset-2026":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        cleared_count = 0
        
        # Clear Redis
        if REDIS_AVAILABLE and redis_client:
            try:
                keys = redis_client.keys("license:*")
                for key in keys:
                    redis_client.delete(key)
                cleared_count += len(keys)
                print(f"✅ Cleared {len(keys)} licenses from Redis")
            except Exception as e:
                print(f"⚠️ Redis clear failed: {e}")
        
        # Clear Memory
        licenses_memory.clear()
        print("✅ Cleared memory storage")
        
        return {
            "success": True,
            "message": f"System reset successful. Cleared {cleared_count} licenses.",
            "note": "Supabase user data retained for analytics"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



