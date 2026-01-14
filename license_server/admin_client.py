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
            api_url="https://shadow-watch-rust.vercel.app",
            admin_secret="your_admin_secret"
        )
        
        # Generate Pro license
        license = await admin.create_pro_license(user_id="user_123")
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
    
    async def create_pro_license(
        self,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Generate Pro license
        
        Returns:
            {
                "license_key": "SW-PRO-...",
                "license_type": "PRO",
                "expires_at": "2027-01-14T00:00:00Z",
                "offline_token": "SW-PRO.<payload>.<sig>"
            }
        """
        path = "/license/pro"
        headers = self._admin_headers("POST", path)
        
        response = await self.client.post(
            f"{self.api_url}{path}",
            json={"user_id": user_id, "metadata": metadata},
            headers=headers
        )
        
        response.raise_for_status()
        return response.json()
    
    async def create_enterprise_license(
        self,
        user_id: str,
        capabilities: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Generate Enterprise license
        
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
        path = "/license/enterprise"
        headers = self._admin_headers("POST", path)
        
        response = await self.client.post(
            f"{self.api_url}{path}",
            json={
                "user_id": user_id,
                "capabilities": capabilities,
                "metadata": metadata
            },
        )
    
    async def create_invariant_license(self, user_id: str, metadata: dict = None) -> Dict:
        """
        Generate Invariant license (365 days, 100K events/month)
        """
        return await self._admin_request(
            "POST",
            "/api/v1/license/invariant",
            {"user_id": user_id, "metadata": metadata}
        )
    
    async def revoke_license(self, license_key: str) -> Dict:
        """
        Revoke a license immediately
            f"{self.api_url}{path}",
            json={"license_key": license_key},
            headers=headers
        )
        
        response.raise_for_status()
        return response.json()
    
    async def validate_license(self, license_key: str) -> Dict:
        """
        """
        Validate a license (admin can call without rate limits)
        
        Returns license details including capabilities
        """
        response = await self.client.post(
            f"{self.api_url}/license/validate",
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
    
    # Create Pro license
    print("\n📝 Creating Pro license...")
    pro_license = await admin.create_pro_license(user_id="user_123")
    print(f"✅ License key: {pro_license['license_key']}")
    print(f"   Expires: {pro_license['expires_at']}")
    
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
