"""
License verification for Shadow Watch

Communicates with license server to verify validity
"""

import httpx
from typing import Dict


async def verify_license_key(
    license_key: str,
    license_server_url: str = "https://shadow-watch-ten.vercel.app"
) -> Dict:
    """
    Verify license key with Shadow Watch license server
    
    Returns:
        {
            "valid": bool,
            "tier": str,
            "max_events": int,
            "customer": str,
            "expires_at": str
        }
    
    Or if invalid:
        {
            "valid": False,
            "error": str
        }
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{license_server_url}/api/v1/license/validate",
                json={"license_key": license_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Map server response to expected format
                return {
                    "valid": data.get("valid", False),
                    "tier": data.get("license_type", "unknown").lower(),
                    "customer": "valued_customer",  # Server doesn't return this yet
                    "expires_at": data.get("expires_at", ""),
                    "max_events": 100000  # Default for Invariant tier
                }
            else:
                return {
                    "valid": False,
                    "error": f"License verification failed: HTTP {response.status_code}"
                }
    
    except httpx.TimeoutException:
        return {
            "valid": False,
            "error": "License server timeout (check internet connection)"
        }
    
    except Exception as e:
        return {
            "valid": False,
            "error": f"License verification error: {str(e)}"
        }


async def report_usage(
    license_key: str,
    events_count: int,
    license_server_url: str = "https://license-shadowwatch.railway.app"
):
    """
    Report usage to license server (called once per day)
    """
    try:
        from datetime import datetime, timezone
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{license_server_url}/report",
                json={
                    "license_key": license_key,
                    "events_count": events_count,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
    except Exception:
        # Silent fail - usage reporting is not critical
        pass
