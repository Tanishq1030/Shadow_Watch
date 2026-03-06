"""
Shadow Watch - Behavioral Intelligence for Your Application

"Like a shadow — always there, never seen."

A passive behavioral intelligence system, fully free and open source.

Features:
- Builds user interest profiles (personalization engine)
- Tracks user activity (behavioral analytics)
- Generates behavioral fingerprints (user understanding)
- Temporal continuity measurement (ATO detection)
- Behavioral divergence detection (compromise detection)
- Pre-auth intent analysis (credential stuffing prevention)

Usage:
    from shadowwatch import ShadowWatch

    sw = ShadowWatch(database_url="postgresql+asyncpg://...")

    # Track activity
    await sw.track(user_id=123, entity_id="AAPL", action="view")

    # Get user profile
    profile = await sw.get_profile(user_id=123)

    # ATO detection
    continuity = await sw.calculate_continuity("user_123")
"""

__version__ = "2.0.0"
__author__ = "Tanishq"
__license__ = "MIT"

from shadowwatch.main import ShadowWatch

__all__ = ["ShadowWatch"]
