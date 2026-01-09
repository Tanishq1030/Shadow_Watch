"""
Shadow Watch - Behavioral Intelligence for Your Application

"Like a shadow — always there, never seen."

A passive behavioral biometric system that:
- Builds user interest profiles (personalization engine)
- Generates behavioral fingerprints (anti-fraud layer)
- Calculates trust scores (adaptive authentication)
- Predicts user intent (recommendation system)
- Detects anomalies (security monitoring)

Usage:
    from shadowwatch import ShadowWatch
    
    sw = ShadowWatch(
        database_url="postgresql://...",
        license_key="SW-XXXX-XXXX-XXXX-XXXX"  # Get trial key from shadowwatch.dev
    )
    
    # Track activity
    await sw.track(user_id=123, entity_id="AAPL", action="view")
    
    # Get user profile
    profile = await sw.get_profile(user_id=123)
    
    # Verify login (trust score)
    trust = await sw.verify_login(
        user_id=123,
        request_context={"ip": "...", "device_fingerprint": "..."}
    )
"""

__version__ = "0.1.0"
__author__ = "Tanishq"
__license__ = "MIT"

from shadowwatch.main import ShadowWatch

__all__ = ["ShadowWatch"]
