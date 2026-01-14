"""
Admin Client - HMAC Request Helper

Helper for making authenticated admin requests to license server.
"""

import time
import hmac
import hashlib
import httpx
from typing import Optional, Dict


class AdminClient:
    """
    Admin client for Shadow Watch License Server
    
    Handles HMAC signature generation for admin endpoints.
    
    Usage:
        admin = AdminClient(
            api_url="https://shadow-watch-ten.vercel.app",
            admin_secret="your_admin_secret"
        )
        
        # Generate Invariant license
        license = await admin.create_invariant_license(user_id="user_123")
        print(license["license_key"])
    """
    
    def __init__(self, api_url: str, admin_secret: str):
        self.api_url = api_url.rstrip("/")
        self.admin_secret = admin_secret.encode()
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _generate_signature(self, method: str, path: str, timestamp: int) -> str:
        """Generate HMAC signature for admin request"""
        msg = f"{method}{path}{timestamp}".encode()
        return hmac.new(self.admin_secret, msg, hashlib.sha256).hexdigest()
    
    def _admin_headers(self, method: str, path: str) -> Dict[str, str]:
        """Generate admin authentication headers"""
        ts = int(time.time())
        sig = self._generate_signature(method, path, ts)
        
        return {
            "X-Admin-Timestamp": str(ts),
            "X-Admin-Signature": sig
        }
    
    async def _admin_request(self, method: str, path: str, data: dict) -> Dict:
        """Make authenticated admin request"""
        headers = self._admin_headers(method, path)
        
        response = await self.client.post(
            f"{self.api_url}{path}",
            json=data,
            headers=headers
        )
        
        response.raise_for_status()
        return response.json()
    
    async def create_invariant_license(
        self,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Generate Invariant license (365 days, 100K events/month)
        
        Returns:
            {
                "license_key": "SW-INV-v1-...",
                "license_type": "INVARIANT",
                "expires_at": "2027-01-14T00:00:00Z",
                "offline_token": "SW-PRO.<payload>.<sig>"
            }
        """
        return await self._admin_request(
            "POST",
            "/api/v1/license/invariant",
            {"user_id": user_id, "metadata": metadata}
        )
    
    async def create_enterprise_license(
        self,
        user_id: str,
        capabilities: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Generate Enterprise license (3 years, custom capabilities)
        
        Args:
            user_id: User identifier
            capabilities: Enterprise capabilities
                {
                    "max_users": 1000,
                    "offline_validation": True,
                    "sso": True,
                    "audit_logs": True,
                    "rate_limit_multiplier": 5
                }
        
        Returns:
            Enterprise license details
        """
        return await self._admin_request(
            "POST",
            "/api/v1/license/enterprise",
            {
                "user_id": user_id,
                "capabilities": capabilities,
                "metadata": metadata
            }
        )
    
    async def revoke_license(self, license_key: str) -> Dict:
        """
        Revoke a license immediately
        
        Returns:
            {
                "status": "revoked",
                "license_key": "SW-INV-v1-...",
                "revoked_at": "2026-01-14T16:22:21Z"
            }
        """
        return await self._admin_request(
            "POST",
            "/api/v1/license/revoke",
            {"license_key": license_key}
        )
    
    async def validate_license(self, license_key: str) -> Dict:
        """
        Validate a license (admin can call without rate limits)
        
        Returns license details including capabilities
        """
        response = await self.client.post(
            f"{self.api_url}/api/v1/license/validate",
            json={"license_key": license_key}
        )
        
        response.raise_for_status()
        return response.json()


# CLI Usage Example
async def main():
    """Example admin usage"""
    import asyncio
    import os
    
    admin = AdminClient(
        api_url=os.getenv("LICENSE_SERVER_URL", "http://localhost:8000"),
        admin_secret=os.getenv("ADMIN_SECRET", "CHANGE_IN_PRODUCTION")
    )
    
    # Create Invariant license
    print("\n📝 Creating Invariant license...")
    inv_license = await admin.create_invariant_license(user_id="user_123")
    print(f"✅ License key: {inv_license['license_key']}")
    print(f"   Expires: {inv_license['expires_at']}")
    
    # Create Enterprise license
    print("\n🏢 Creating Enterprise license...")
    ent_license = await admin.create_enterprise_license(
        user_id="enterprise_corp",
        capabilities={
            "max_users": 1000,
            "offline_validation": True,
            "sso": True,
            "audit_logs": True,
            "rate_limit_multiplier": 5
        }
    )
    print(f"✅ License key: {ent_license['license_key']}")
    print(f"   Capabilities: {ent_license['capabilities']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
