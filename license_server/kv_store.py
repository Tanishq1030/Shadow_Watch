"""
Vercel KV (Redis) License Storage

Replaces SQLite with Redis for serverless compatibility.
Works with both Vercel KV (production) and local Redis (development).
"""

import os
import json
from typing import Optional, Dict, List
from datetime import datetime

# Try to connect to Redis
try:
    from redis import Redis
    
    # Use Vercel KV URL if available, otherwise local Redis
    redis_url = os.getenv("KV_REST_API_URL", "redis://localhost:6379")
    redis_client = Redis.from_url(redis_url, decode_responses=True)
    
    # Test connection
    redis_client.ping()
    print(f"✅ Connected to Redis: {redis_url}")
    
except Exception as e:
    print(f"⚠️ Redis not available: {e}")
    print("   Using in-memory fallback (NOT for production!)")
    redis_client = None


class LicenseStore:
    """
    Redis-based license storage
    
    Responsibility:
    - Store/retrieve license keys from Redis (Vercel KV)
    - Handle usage reporting
    - Provide stats/analytics
    """
    
    # In-memory fallback (for testing without Redis)
    _memory_store: Dict[str, Dict] = {}
    _memory_usage: Dict[str, List] = {}
    
    @staticmethod
    def _use_redis() -> bool:
        """Check if Redis is available"""
        return redis_client is not None
    
    @staticmethod
    def _license_key_to_redis_key(license_key: str) -> str:
        """Convert license key to Redis key"""
        return f"license:{license_key}"
    
    @staticmethod
    def save_license(
        license_key: str,
        tier: str,
        max_events: int,
        customer_name: str = "Trial User",
        customer_email: str = "",
        expires_at: str = "",
    ) -> bool:
        """
        Save license to Redis
        
        Args:
            license_key: Unique license key
            tier: License tier (trial, pro, enterprise)
            max_events: Maximum events allowed
            customer_name: Customer name
            customer_email: Customer email
            expires_at: Expiration date (ISO format)
        
        Returns:
            True if saved successfully
        """
        license_data = {
            "license_key": license_key,
            "tier": tier,
            "max_events": max_events,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at,
            "is_active": True
        }
        
        try:
            if LicenseStore._use_redis():
                # Store in Redis
                redis_key = LicenseStore._license_key_to_redis_key(license_key)
                redis_client.set(redis_key, json.dumps(license_data))
                
                # Add to index
                redis_client.sadd("license:index", license_key)
            else:
                # Fallback: in-memory
                LicenseStore._memory_store[license_key] = license_data
            
            return True
            
        except Exception as e:
            print(f"Error saving license: {e}")
            return False
    
    @staticmethod
    def get_license(license_key: str) -> Optional[Dict]:
        """
        Get license from Redis
        
        Args:
            license_key: License key to retrieve
        
        Returns:
            License data dict or None if not found
        """
        try:
            if LicenseStore._use_redis():
                redis_key = LicenseStore._license_key_to_redis_key(license_key)
                data = redis_client.get(redis_key)
                
                if data:
                    return json.loads(data)
                return None
            else:
                # Fallback: in-memory
                return LicenseStore._memory_store.get(license_key)
                
        except Exception as e:
            print(f"Error getting license: {e}")
            return None
    
    @staticmethod
    def delete_license(license_key: str) -> bool:
        """Delete/deactivate license"""
        try:
            if LicenseStore._use_redis():
                redis_key = LicenseStore._license_key_to_redis_key(license_key)
                redis_client.delete(redis_key)
                redis_client.srem("license:index", license_key)
            else:
                # Fallback: in-memory
                LicenseStore._memory_store.pop(license_key, None)
            
            return True
            
        except Exception as e:
            print(f"Error deleting license: {e}")
            return False
    
    @staticmethod
    def list_all_licenses() -> List[Dict]:
        """List all licenses"""
        try:
            if LicenseStore._use_redis():
                license_keys = redis_client.smembers("license:index")
                licenses = []
                
                for key in license_keys:
                    license_data = LicenseStore.get_license(key)
                    if license_data:
                        licenses.append(license_data)
                
                return licenses
            else:
                # Fallback: in-memory
                return list(LicenseStore._memory_store.values())
                
        except Exception as e:
            print(f"Error listing licenses: {e}")
            return []
    
    @staticmethod
    def report_usage(license_key: str, events_count: int, timestamp: str):
        """
        Store usage report
        
        Args:
            license_key: License key
            events_count: Number of events
            timestamp: Report timestamp
        """
        report_data = {
            "license_key": license_key,
            "events_count": events_count,
            "timestamp": timestamp
        }
        
        try:
            if LicenseStore._use_redis():
                report_key = f"usage:{license_key}:{timestamp}"
                redis_client.set(report_key, json.dumps(report_data))
                redis_client.sadd(f"usage:index:{license_key}", report_key)
            else:
                # Fallback: in-memory
                if license_key not in LicenseStore._memory_usage:
                    LicenseStore._memory_usage[license_key] = []
                LicenseStore._memory_usage[license_key].append(report_data)
            
            return True
            
        except Exception as e:
            print(f"Error reporting usage: {e}")
            return False
    
    @staticmethod
    def get_total_events(license_key: str) -> int:
        """Get total events for a license"""
        try:
            if LicenseStore._use_redis():
                report_keys = redis_client.smembers(f"usage:index:{license_key}")
                total = 0
                
                for key in report_keys:
                    data = redis_client.get(key)
                    if data:
                        report = json.loads(data)
                        total += report.get("events_count", 0)
                
                return total
            else:
                # Fallback: in-memory
                reports = LicenseStore._memory_usage.get(license_key, [])
                return sum(r.get("events_count", 0) for r in reports)
                
        except:
            return 0
