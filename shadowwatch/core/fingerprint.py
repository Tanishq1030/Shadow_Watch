"""
Behavioral Fingerprinting

Generates unique behavioral signatures from user activity patterns
"""

from sqlalchemy.ext.asyncio import AsyncSession
from shadowwatch.core.scorer import generate_library_snapshot


async def verify_fingerprint(
    db: AsyncSession,
    user_id: int,
    client_fingerprint: str
) -> float:
    """
    Compare client fingerprint with expected Shadow Watch fingerprint
    
    Args:
        db: Database session (injected by caller)
        user_id: User identifier
        client_fingerprint: Fingerprint submitted by client (from cache/localStorage)
    
    Returns:
        Match score (0.0-1.0)
        - 1.0 = Perfect match (user behavior intact)
        - 0.5 = Neutral (new device/cleared cache)
        - 0.3 = Mismatch (SUSPICIOUS - possible account takeover)
    
    Responsibility:
    - Generate current fingerprint from user's library
    - Compare with submitted fingerprint
    - Return match confidence score
    
    Usage:
    Called by trust_score.py during login verification
    """
    current_snapshot = await generate_library_snapshot(db, user_id)
    expected_fingerprint = current_snapshot["fingerprint"]
    
    if client_fingerprint == expected_fingerprint:
        return 1.0  # Perfect match
    
    if not client_fingerprint:
        return 0.5  # Neutral (no fingerprint provided)
    
    return 0.3  # Mismatch (suspicious)
