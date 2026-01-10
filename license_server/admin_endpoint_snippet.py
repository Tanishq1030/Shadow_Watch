
@app.post("/admin/generate-keys")
async def admin_generate_keys(count: int = 10):
    """
    Admin endpoint: Generate trial license keys
    
    Usage:
        curl -X POST "https://your-server.com/admin/generate-keys?count=10"
    
    Args:
        count: Number of trial keys to generate (default: 10)
    
    Returns:
        JSON with generated keys and expiration date
    """
    import secrets
    import string
    from datetime import timedelta
    
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
    
    return {
        "success": True,
        "generated": len(created_keys),
        "expires_at": expires_at[:10],
        "max_events": 10000,
        "keys": created_keys
    }
