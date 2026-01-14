"""
Shadow Watch - Behavioral Intelligence for Your Application

"Like a shadow — always there, never seen."

A passive behavioral biometric system with:

FREE TIER (no license needed):
- Builds user interest profiles (personalization engine)
- Tracks user activity (behavioral analytics)
- Generates behavioral profiles (user understanding)

INVARIANT TIER (requires license):
- Temporal continuity measurement (ATO detection)
- Behavioral divergence detection (compromise detection)
- Pre-auth intent analysis (credential stuffing prevention)

Usage:
    from shadowwatch import ShadowWatch
    
    # Free tier (no license needed)
    sw = ShadowWatch(database_url="postgresql://...")
    
    # Track activity
    await sw.track(user_id=123, entity_id="AAPL", action="view")
    
    # Get user profile
    profile = await sw.get_profile(user_id=123)
    
    # Invariant tier (requires license)
    sw = ShadowWatch(
        database_url="postgresql://...",
        license_key="SW-INV-v1-XXXX-XXXX-XXXX"  
    )
    continuity = await sw.calculate_continuity("user_123")
"""

__version__ = "1.0.0"
__author__ = "Tanishq"
__license__ = "MIT"

from shadowwatch.main import ShadowWatch
from shadowwatch.exceptions import LicenseError

__all__ = ["ShadowWatch", "LicenseError"]
