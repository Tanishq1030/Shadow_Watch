"""
License Management Routes - Invariant Implementation

Endpoints:
- POST /license/invariant - Generate Invariant license (admin)
- POST /license/enterprise - Generate Enterprise license (admin)
- POST /license/validate - Validate any license
- POST /license/revoke - Revoke a license (admin)
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import secrets
import hmac
import hashlib
import base64
import json
import time

from ..database import get_db
from ..kv_store import redis
from ..auth import verify_admin

router = APIRouter(prefix="/license", tags=["licenses"])

# Constants
TRIAL_DURATION_DAYS = 30
INVARIANT_DURATION_DAYS = 365
ENTERPRISE_DURATION_DAYS = 365 * 3
OFFLINE_LICENSE_SECRET = b"OFFLINE_LICENSE_SECRET_CHANGE_IN_PRODUCTION"


# ============================================================
# Models
# ============================================================

class LicenseRequest(BaseModel):
    user_id: str
    metadata: Optional[Dict] = None


class EnterpriseLicenseRequest(BaseModel):
    user_id: str
    capabilities: Dict
    metadata: Optional[Dict] = None


class ValidateRequest(BaseModel):
    license_key: str


class RevokeRequest (BaseModel):
    license_key: str


# ============================================================
# License Key Generation
# ============================================================

def generate_license_key(prefix: str = "SW-INV-v1") -> str:
    """
    Generate cryptographically secure license key
    
    Format: SW-INV-v1-<24 hex chars>
    Example: SW-INV-v1-9f3a8c2d7e4b1a0c8d91f2a34b6c
    
    Note: Also supports legacy SW-PRO-* format for backward compatibility
    """
    return f"{prefix}-{secrets.token_hex(12)}"


def sign_offline_payload(payload: dict) -> Tuple[str, str]:
    """
    Sign payload for offline validation
    
    Returns: (payload_b64, signature_b64)
    """
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig = hmac.new(OFFLINE_LICENSE_SECRET, raw, hashlib.sha256).digest()
    
    payload_b64 = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    
    return payload_b64, sig_b64


def create_offline_license(user_id: str, license_type: str, expires_at: datetime) -> str:
    """
    Create offline-capable license token
    
    Format: SW-PRO.<payload>.<signature>
    """
    payload = {
        "iss": "shadow-watch",
        "sub": user_id,
        "lic": license_type,
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int(expires_at.timestamp()),
        "kid": "v1"
    }
    
    payload_b64, sig_b64 = sign_offline_payload(payload)
    
    return f"SW-PRO.{payload_b64}.{sig_b64}"


# ============================================================
# Pro License Generation (Admin Only)
# ============================================================

@router.post("/invariant")
async def create_invariant_license(
    req: LicenseRequest,
    admin: dict = Depends(verify_admin)
):
    """
    Generate Invariant license - ADMIN ONLY
    
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
    
    # Store in database (source of truth)
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO licenses (
                license_key,
                user_id,
                license_type,
                issued_at,
                expires_at,
                metadata,
                is_revoked
            )
            VALUES ($1, $2, $3, $4, $5, $6, false)
            """,
            license_key,
            req.user_id,
            "INVARIANT",
            issued_at,
            expires_at,
            json.dumps(metadata)
        )
    
    # Store in Redis (hot cache)
    ttl_seconds = int((expires_at - issued_at).total_seconds())
    
    await redis.setex(
        f"license:{license_key}",
        ttl_seconds,
        json.dumps({
            "user_id": req.user_id,
            "license_type": "INVARIANT",
            "expires_at": expires_at.isoformat(),
            "revoked": False,
            "metadata": metadata
        })
    )
    
    # Generate offline token (optional)
    offline_token = create_offline_license(req.user_id, "INVARIANT", expires_at)
    
    return {
        "license_key": license_key,
        "license_type": "INVARIANT",
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "metadata": metadata,
        "offline_token": offline_token
    }


# ============================================================
# Enterprise License Generation (Admin Only)
# ============================================================

@router.post("/enterprise")
async def create_enterprise_license(
    req: EnterpriseLicenseRequest,
    admin: dict = Depends(verify_admin)
):
    """
    Generate Enterprise license - ADMIN ONLY
    
    - Duration: 3 years
    - Tier: ENTERPRISE
    - Capabilities: Custom
    """
    license_key = generate_license_key("SW-ENT")
    issued_at = datetime.utcnow()
    expires_at = issued_at + timedelta(days=ENTERPRISE_DURATION_DAYS)
    
    metadata = req.metadata or {}
    metadata["tier"] = "enterprise"
    metadata["capabilities"] = req.capabilities
    
    # Store in database
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO licenses (
                license_key,
                user_id,
                license_type,
                issued_at,
                expires_at,
                metadata,
                is_revoked
            )
            VALUES ($1, $2, $3, $4, $5, $6, false)
            """,
            license_key,
            req.user_id,
            "ENTERPRISE",
            issued_at,
            expires_at,
            json.dumps(metadata)
        )
    
    # Store in Redis
    ttl_seconds = int((expires_at - issued_at).total_seconds())
    
    await redis.setex(
        f"license:{license_key}",
        ttl_seconds,
        json.dumps({
            "user_id": req.user_id,
            "license_type": "ENTERPRISE",
            "expires_at": expires_at.isoformat(),
            "revoked": False,
            "capabilities": req.capabilities,
            "metadata": metadata
        })
    )
    
    # Generate offline token
    offline_token = create_offline_license(req.user_id, "ENTERPRISE", expires_at)
    
    return {
        "license_key": license_key,
        "license_type": "ENTERPRISE",
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "capabilities": req.capabilities,
        "offline_token": offline_token
    }


# ============================================================
# License Validation (Public)
# ============================================================

@router.post("/validate")
async def validate_license(req: ValidateRequest):
    """
    Validate license key
    
    Hot path: Redis → Database
    Fail closed on ambiguity
    """
    license_key = req.license_key
    
    # 1. Try Redis (hot path)
    cached = await redis.get(f"license:{license_key}")
    
    if cached:
        data = json.loads(cached)
        
        # Check revocation
        if data.get("revoked"):
            raise HTTPException(403, "License revoked")
        
        # Check expiration
        expires_at = datetime.fromisoformat(data["expires_at"])
        if expires_at < datetime.utcnow():
            raise HTTPException(403, "License expired")
        
        return {
            "valid": True,
            "license_type": data["license_type"],
            "user_id": data["user_id"],
            "expires_at": data["expires_at"],
            "capabilities": data.get("capabilities"),
            "metadata": data.get("metadata")
        }
    
    # 2. Fallback to database
    async with get_db() as db:
        row = await db.fetchrow(
            """
            SELECT 
                user_id,
                license_type,
                expires_at,
                is_revoked,
                metadata
            FROM licenses
            WHERE license_key = $1
            """,
            license_key
        )
    
    if not row:
        raise HTTPException(403, "Invalid license")
    
    if row["is_revoked"]:
        raise HTTPException(403, "License revoked")
    
    if row["expires_at"] < datetime.utcnow():
        raise HTTPException(403, "License expired")
    
    # Parse metadata
    metadata = json.loads(row["metadata"]) if row["metadata"] else {}
    
    # Cache in Redis for future requests
    ttl_seconds = int((row["expires_at"] - datetime.utcnow()).total_seconds())
    
    cache_data = {
        "user_id": row["user_id"],
        "license_type": row["license_type"],
        "expires_at": row["expires_at"].isoformat(),
        "revoked": False,
        "capabilities": metadata.get("capabilities"),
        "metadata": metadata
    }
    
    await redis.setex(
        f"license:{license_key}",
        ttl_seconds,
        json.dumps(cache_data)
    )
    
    return {
        "valid": True,
        "license_type": row["license_type"],
        "user_id": row["user_id"],
        "expires_at": row["expires_at"].isoformat(),
        "capabilities": metadata.get("capabilities"),
        "metadata": metadata
    }


# ============================================================
# License Revocation (Admin Only)
# ============================================================

@router.post("/revoke")
async def revoke_license(
    req: RevokeRequest,
    admin: dict = Depends(verify_admin)
):
    """
    Revoke a license immediately - ADMIN ONLY
    
    - Updates database (source of truth)
    - Updates Redis (hot path)
    - No grace period
    """
    license_key = req.license_key
    
    # Update database
    async with get_db() as db:
        result = await db.execute(
            """
            UPDATE licenses
            SET is_revoked = true
            WHERE license_key = $1
            """,
            license_key
        )
    
    # Update Redis if cached
    cached = await redis.get(f"license:{license_key}")
    
    if cached:
        data = json.loads(cached)
        data["revoked"] = True
        
        # Keep existing TTL
        ttl = await redis.ttl(f"license:{license_key}")
        
        await redis.setex(
            f"license:{license_key}",
            ttl if ttl > 0 else 3600,
            json.dumps(data)
        )
    
    return {
        "status": "revoked",
        "license_key": license_key,
        "revoked_at": datetime.utcnow().isoformat()
    }
