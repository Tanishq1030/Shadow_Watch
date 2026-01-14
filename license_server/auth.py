"""
Admin Authentication - HMAC-Based

Secure admin endpoints with HMAC signature verification.
No tokens to leak, replay-safe, simple to rotate.
"""

from fastapi import Request, HTTPException
import hmac
import hashlib
import time
import os

# Admin secret (load from environment in production)
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "CHANGE_IN_PRODUCTION").encode()

# Request freshness window (30 seconds)
TIMESTAMP_TOLERANCE = 30


async def verify_admin(request: Request) -> dict:
    """
    Verify admin request using HMAC signature
    
    Headers required:
    - X-Admin-Timestamp: Unix timestamp
    - X-Admin-Signature: HMAC-SHA256 signature
    
    Signature base: {method}{path}{timestamp}
    
    Example:
        POST/license/pro1700000000
        → HMAC-SHA256(ADMIN_SECRET, "POST/license/pro1700000000")
    
    Raises:
        HTTPException 401: Stale request (timestamp too old/new)
        HTTPException 403: Invalid signature
    """
    # Get headers
    ts_header = request.headers.get("X-Admin-Timestamp")
    sig_header = request.headers.get("X-Admin-Signature")
    
    if not ts_header or not sig_header:
        raise HTTPException(
            status_code=403,
            detail="Missing admin authentication headers"
        )
    
    # Parse timestamp
    try:
        ts = int(ts_header)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Invalid timestamp format"
        )
    
    # Check timestamp freshness (prevent replay attacks)
    now = int(time.time())
    
    if abs(now - ts) > TIMESTAMP_TOLERANCE:
        raise HTTPException(
            status_code=401,
            detail=f"Request timestamp too old/new (tolerance: {TIMESTAMP_TOLERANCE}s)"
        )
    
    # Construct signature base
    msg = f"{request.method}{request.url.path}{ts}".encode()
    
    # Compute expected signature
    expected_sig = hmac.new(ADMIN_SECRET, msg, hashlib.sha256).hexdigest()
    
    # Compare signatures (constant-time to prevent timing attacks)
    if not hmac.compare_digest(sig_header, expected_sig):
        raise HTTPException(
            status_code=403,
            detail="Invalid admin signature"
        )
    
    # Return admin context (can be extended later)
    return {
        "authenticated": True,
        "timestamp": ts
    }


def generate_admin_signature(method: str, path: str, timestamp: int) -> str:
    """
    Generate admin signature (for client-side use)
    
    Usage:
        ts = int(time.time())
        sig = generate_admin_signature("POST", "/license/pro", ts)
        
        headers = {
            "X-Admin-Timestamp": str(ts),
            "X-Admin-Signature": sig
        }
    """
    msg = f"{method}{path}{timestamp}".encode()
    return hmac.new(ADMIN_SECRET, msg, hashlib.sha256).hexdigest()
