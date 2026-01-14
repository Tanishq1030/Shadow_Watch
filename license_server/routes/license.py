"""
License Routes - Supabase Client Version

Simplified for Vercel serverless using Supabase client
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import secrets

from database import get_db
from kv_store import redis_kv
from auth import verify_admin

router = APIRouter(prefix="/api/v1/license", tags=["licenses"])

# Constants
TRIAL_DURATION_DAYS = 30
INVARIANT_DURATION_DAYS = 365
ENTERPRISE_DURATION_DAYS = 1095  # 3 years


# Request models
class InvariantLicenseRequest(BaseModel):
    user_id: str
    metadata: Optional[dict] = None


class EnterpriseLicenseRequest(BaseModel):
    user_id: str
    capabilities: dict
    metadata: Optional[dict] = None


class RevokeLicenseRequest(BaseModel):
    license_key: str


class ValidateLicenseRequest(BaseModel):
    license_key: str


def generate_license_key(prefix: str = "SW-INV-v1") -> str:
    """Generate secure license key"""
    random_part = secrets.token_hex(12)  # 24 hex chars
    return f"{prefix}-{random_part}"


@router.post("/invariant", dependencies=[Depends(verify_admin)])
async def create_invariant_license(req: InvariantLicenseRequest):
    """
    Generate Invariant license (Admin only)
    
    - Duration: 365 days
    - Tier: INVARIANT
    - Max events: 100,000/month
    """
    license_key = generate_license_key("SW-INV-v1")
    issued_at = datetime.utcnow()
    expires_at = issued_at + timedelta(days=INVARIANT_DURATION_DAYS)
    
    metadata = req.metadata or {}
    metadata["tier"] = "invariant"
    metadata["max_events"] = 100000
    
    # Get Supabase client
    db = await get_db()
    
    # Insert license using Supabase client
    try:
        result = db.table("licenses").insert({
            "license_key": license_key,
            "user_id": req.user_id,
            "license_type": "INVARIANT",
            "issued_at": issued_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "metadata": metadata,
            "is_revoked": False,
            "created_at": issued_at.isoformat()
        }).execute()
        
        # Cache in Redis
        await redis_kv.set(
            f"license:{license_key}",
            {
                "license_type": "INVARIANT",
                "expires_at": expires_at.isoformat(),
                "is_revoked": False,
                "user_id": req.user_id
            },
            ttl=86400  # 24 hours
        )
        
        return {
            "license_key": license_key,
            "license_type": "INVARIANT",
            "user_id": req.user_id,
            "issued_at": issued_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "metadata": metadata
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/enterprise", dependencies=[Depends(verify_admin)])
async def create_enterprise_license(req: EnterpriseLicenseRequest):
    """
    Generate Enterprise license (Admin only)
    
    - Duration: 1095 days (3 years)
    - Tier: ENTERPRISE
    - Custom capabilities
    """
    license_key = generate_license_key("SW-ENT-v1")
    issued_at = datetime.utcnow()
    expires_at = issued_at + timedelta(days=ENTERPRISE_DURATION_DAYS)
    
    metadata = req.metadata or {}
    metadata["tier"] = "enterprise"
    metadata["capabilities"] = req.capabilities
    
    # Get Supabase client
    db = await get_db()
    
    try:
        result = db.table("licenses").insert({
            "license_key": license_key,
            "user_id": req.user_id,
            "license_type": "ENTERPRISE",
            "issued_at": issued_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "metadata": metadata,
            "is_revoked": False,
            "created_at": issued_at.isoformat()
        }).execute()
        
        # Cache in Redis
        await redis_kv.set(
            f"license:{license_key}",
            {
                "license_type": "ENTERPRISE",
                "expires_at": expires_at.isoformat(),
                "is_revoked": False,
                "capabilities": req.capabilities
            },
            ttl=86400
        )
        
        return {
            "license_key": license_key,
            "license_type": "ENTERPRISE",
            "user_id": req.user_id,
            "issued_at": issued_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "capabilities": req.capabilities,
            "metadata": metadata
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/validate")
async def validate_license(req: ValidateLicenseRequest):
    """
    Validate license key (Public endpoint)
    
    Returns license status and metadata
    """
    license_key = req.license_key
    
    # Check cache first
    cached = await redis_kv.get(f"license:{license_key}")
    if cached:
        # Verify not expired
        expires_at = datetime.fromisoformat(cached["expires_at"])
        if datetime.utcnow() > expires_at:
            return {"valid": False, "reason": "License expired"}
        
        if cached.get("is_revoked"):
            return {"valid": False, "reason": "License revoked"}
        
        return {
            "valid": True,
            "license_type": cached["license_type"],
            "expires_at": cached["expires_at"]
        }
    
    # Query database
    db = await get_db()
    
    try:
        result = db.table("licenses").select("*").eq("license_key", license_key).execute()
        
        if not result.data:
            return {"valid": False, "reason": "License not found"}
        
        license_data = result.data[0]
        
        # Check expiry
        expires_at = datetime.fromisoformat(license_data["expires_at"])
        if datetime.utcnow() > expires_at:
            return {"valid": False, "reason": "License expired"}
        
        # Check revoked
        if license_data.get("is_revoked"):
            return {"valid": False, "reason": "License revoked"}
        
        # Cache for future requests
        await redis_kv.set(
            f"license:{license_key}",
            {
                "license_type": license_data["license_type"],
                "expires_at": license_data["expires_at"],
                "is_revoked": license_data["is_revoked"]
            },
            ttl=86400
        )
        
        return {
            "valid": True,
            "license_type": license_data["license_type"],
            "expires_at": license_data["expires_at"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post("/revoke", dependencies=[Depends(verify_admin)])
async def revoke_license(req: RevokeLicenseRequest):
    """
    Revoke license immediately (Admin only)
    """
    license_key = req.license_key
    
    # Get Supabase client
    db = await get_db()
    
    try:
        # Update database
        result = db.table("licenses").update({
            "is_revoked": True,
            "revoked_at": datetime.utcnow().isoformat()
        }).eq("license_key", license_key).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="License not found")
        
        # Invalidate cache
        await redis_kv.delete(f"license:{license_key}")
        
        return {
            "status": "revoked",
            "license_key": license_key,
            "revoked_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revocation error: {str(e)}")
