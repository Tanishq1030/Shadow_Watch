"""
Behavioral Fingerprinting

Computes a continuous behavioral similarity score using Jaccard set
similarity over the user's top entity set rather than a binary
SHA-256 hash comparison.

Why Jaccard?
- A user who added one new stock to their watchlist should NOT score 0.3
  (suspicious). They are still clearly the same person.
- Jaccard returns 0.9 for 90% overlap, 0.0 for zero overlap.
- This maps naturally onto the trust_score weight (20%) as a real signal.
"""

from typing import Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

# Number of top entities to include in the comparison set
TOP_N = 10


async def _get_top_entities(db: AsyncSession, user_id: int) -> Set[str]:
    """
    Fetch the top-N most active entity IDs for a user.

    Uses the UserInterest table (aggregated scores) so it reflects
    the user's long-term behavioral pattern, not just recent events.
    """
    from shadowwatch.models.interest import UserInterest

    result = await db.execute(
        select(UserInterest.symbol)
        .where(UserInterest.user_id == user_id)
        .order_by(desc(UserInterest.score))
        .limit(TOP_N)
    )
    return {row[0] for row in result.fetchall()}


def _jaccard_similarity(a: Set[str], b: Set[str]) -> float:
    """
    Jaccard similarity coefficient between two sets.

    J(A, B) = |A ∩ B| / |A ∪ B|

    Returns:
        float ∈ [0.0, 1.0]
        1.0 = identical sets
        0.0 = completely disjoint
    """
    if not a and not b:
        return 1.0  # Both empty → trivially the same
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union


async def verify_fingerprint(
    db: AsyncSession,
    user_id: int,
    client_top_entities: Optional[Set[str]] = None,
) -> float:
    """
    Calculate behavioral fingerprint match score using Jaccard similarity.

    Compares the user's current top-N entity set (from DB) against a
    client-supplied set of entities to produce a continuous similarity score.

    Args:
        db:                   SQLAlchemy async session
        user_id:              User identifier
        client_top_entities:  Set of entity IDs known to the client
                              (e.g. from a cached library snapshot).
                              Pass None / empty if unavailable.

    Returns:
        float ∈ [0.0, 1.0]
        1.0   — perfect overlap (same actor, high confidence)
        ~0.7  — strong overlap (minor behavioural drift, still likely same actor)
        ~0.4  — moderate overlap (significant change, flag for review)
        0.0   — zero overlap (likely different actor, high ATO risk)
        0.5   — neutral fallback when client provides no entities

    Called by:
        trust_score.py during verify_login()
    """
    # Fetch the server-side top entity set
    server_entities = await _get_top_entities(db, user_id)

    # No history yet — benefit of the doubt (new user)
    if not server_entities:
        return 0.7

    # Client provided no data — neutral (e.g. new device, cleared cache)
    if not client_top_entities:
        return 0.5

    return _jaccard_similarity(server_entities, client_top_entities)
