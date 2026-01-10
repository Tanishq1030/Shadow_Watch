"""
Generate Trial License Keys (Redis/Vercel KV version)

Works with both:
- Vercel KV (production)
- Local Redis (development) 
- In-memory fallback (testing without Redis)
"""

import secrets
import string
from datetime import datetime, timedelta
from kv_store import LicenseStore


def generate_key():
    """Generate unique trial key in format: SW-TRIAL-XXXX-XXXX-XXXX-XXXX"""
    chars = string.ascii_uppercase + string.digits
    parts = [
        ''.join(secrets.choice(chars) for _ in range(4))
        for _ in range(4)
    ]
    return f"SW-TRIAL-{'-'.join(parts)}"


def generate_trial_keys(count=10):
    """
    Generate N trial keys
    
    Args:
        count: Number of keys to generate (default: 10)
    """
    created = 0
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    print(f"\n🔑 Generating {count} trial license keys...")
    print(f"📅 Expiration: {expires_at[:10]} (30 days)")
    print(f"📊 Max events: 10,000 per license\n")
    
    for i in range(count):
        key = generate_key()
        
        success = LicenseStore.save_license(
            license_key=key,
            tier="trial",
            max_events=10000,
            customer_name=f"Trial User {i+1}",
            customer_email="",
            expires_at=expires_at
        )
        
        if success:
            created += 1
            print(f"✅ Generated: {key}")
        else:
            print(f"⚠️  Failed to generate key {i+1}")
    
    print(f"\n🎉 Successfully generated {created}/{count} trial keys")
    
    if created < count:
        print(f"⚠️  {count - created} keys failed (check Redis connection)")


if __name__ == "__main__":
    generate_trial_keys(10)
