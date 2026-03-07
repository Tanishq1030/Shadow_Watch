"""
All five signals (IP, Device, Behavioral, Time, API) are now implemented.
"""

import math
import numpy as np
from datetime import datetime, timezone
from typing import Optional, Set, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from shadowwatch.core.fingerprint import verify_fingerprint


# =====================================================
# Weight definitions
# =====================================================

# Weights (Full ensemble)
WEIGHTS = {
    "ip_location":  0.30,
    "device":       0.25,
    "behavioral":   0.20,
    "time_pattern": 0.15,
    "api_behavior": 0.10,
}



# =====================================================
# Individual signal functions
# =====================================================

async def _score_ip(
    db: AsyncSession,
    user_id: int,
    ip: Optional[str],
    country: Optional[str],
) -> float:
    """
    IP trust factor.

    Rules (in priority order):
        No IP provided                → 0.7  (neutral)
        No IP history (first login)   → 0.7  (benefit of the doubt)
        Known IP                      → 1.0
        New IP, same country          → 0.65
        New IP, new country           → 0.4
    """
    if not ip:
        return 0.7

    from shadowwatch.models.ip_history import UserIPHistory

    # Look up this specific IP
    result = await db.execute(
        select(UserIPHistory)
        .where(
            UserIPHistory.user_id == user_id,
            UserIPHistory.ip_address == ip,
        )
    )
    known_ip = result.scalar_one_or_none()

    if known_ip:
        # Seen this exact IP before — fully trusted
        return 1.0

    # New IP — check if the country is familiar
    if country:
        country_result = await db.execute(
            select(UserIPHistory)
            .where(
                UserIPHistory.user_id == user_id,
                UserIPHistory.country == country,
            )
            .limit(1)
        )
        same_country = country_result.scalar_one_or_none()

        if same_country:
            return 0.65  # New IP but familiar country

    # No history at all for this user
    count_result = await db.execute(
        select(UserIPHistory).where(UserIPHistory.user_id == user_id).limit(1)
    )
    has_any_history = count_result.scalar_one_or_none() is not None

    if not has_any_history:
        return 0.7  # First-ever login — benefit of the doubt

    return 0.4  # New IP, new country, with existing history → suspicious


async def _score_device(
    db: AsyncSession,
    user_id: int,
    device_fingerprint: Optional[str],
    user_agent: Optional[str],
) -> float:
    """
    Device trust factor.

    Rules:
        No device fingerprint             → 0.6  (neutral-low, can't verify)
        No device history (first login)   → 0.7
        Known fingerprint                 → trust_level stored in DB
        New fingerprint, known UA family  → 0.6
        Completely new device             → 0.45
    """
    if not device_fingerprint:
        return 0.6

    from shadowwatch.models.device import UserDeviceHistory

    # Look up exact device fingerprint
    result = await db.execute(
        select(UserDeviceHistory)
        .where(
            UserDeviceHistory.user_id == user_id,
            UserDeviceHistory.device_fingerprint == device_fingerprint,
        )
    )
    known_device = result.scalar_one_or_none()

    if known_device:
        return float(known_device.trust_level)

    # No history at all
    count_result = await db.execute(
        select(UserDeviceHistory)
        .where(UserDeviceHistory.user_id == user_id)
        .limit(1)
    )
    has_any_history = count_result.scalar_one_or_none() is not None

    if not has_any_history:
        return 0.7  # First-ever login

    return 0.45  # New, unrecognized device


async def _score_time_pattern(
    db: AsyncSession,
    user_id: int,
    dt: datetime,
) -> float:
    """
    Temporal trust factor.
    
    Compares current hour (0-23) against user's historical heatmap.
    If the current hour has high relative density, score is high.
    """
    from shadowwatch.models.heatmap import UserActivityHeatmap
    
    hour = dt.hour
    
    # Fetch user's heatmap
    result = await db.execute(
        select(UserActivityHeatmap).where(UserActivityHeatmap.user_id == user_id)
    )
    history = result.scalars().all()
    
    if not history:
        return 0.7  # No history — neutral
        
    weights = {h.hour: h.weight for h in history}
    total_weight = sum(weights.values())
    
    if total_weight == 0:
        return 0.7
        
    # Relative density at this hour
    current_weight = weights.get(hour, 0.0)
    avg_weight = total_weight / 24.0
    
    # Gaussian-like smoothing: check adjacent hours too
    context_weight = (
        current_weight * 1.0 +
        weights.get((hour - 1) % 24, 0.0) * 0.5 +
        weights.get((hour + 1) % 24, 0.0) * 0.5
    ) / 2.0
    
    # Score is high if context_weight > avg_weight
    score = 0.5 + (context_weight / (avg_weight * 2.0 + 1e-6)) * 0.5
    return float(np.clip(score, 0.3, 1.0))


async def _score_api_behavior(
    db: AsyncSession,
    user_id: int,
) -> float:
    """
    API regularity / Bot detection factor.
    
    Analyzes jitter (variance) in request timing.
    Humans have high jitter; bots have low jitter.
    """
    from shadowwatch.models.activity import UserActivityEvent
    
    # Fetch last 20 events
    result = await db.execute(
        select(UserActivityEvent)
        .where(UserActivityEvent.user_id == user_id)
        .order_by(UserActivityEvent.occurred_at.desc())
        .limit(20)
    )
    events = result.scalars().all()
    
    if len(events) < 5:
        return 1.0  # Not enough data to penalize
        
    # Calculate inter-arrival times (seconds)
    events.sort(key=lambda x: x.occurred_at)
    intervals = []
    for i in range(1, len(events)):
        delta = (events[i].occurred_at - events[i-1].occurred_at).total_seconds()
        if delta > 0:
            intervals.append(delta)
            
    if not intervals:
        return 1.0
        
    # Jitter = Coefficient of Variation (StdDev / Mean)
    mean_int = np.mean(intervals)
    std_int = np.std(intervals)
    
    if mean_int < 0.001: # Way too fast
        return 0.2
        
    cv = std_int / mean_int
    
    # CV < 0.1 indicates extreme regularity (bot)
    # CV > 1.0 indicates human-like randomness (bursty)
    if cv < 0.1:
        return 0.3 # High probability bot
    elif cv < 0.3:
        return 0.6 # Suspiciously regular
        
    return 1.0 # Normal human jitter


# =====================================================
# Main ensemble function
# =====================================================

async def calculate_trust_score(
    db: AsyncSession,
    user_id: int,
    request_context: dict,
) -> dict:
    """
    Calculate ensemble trust score for login / sensitive actions.

    Args:
        db:              Database session
        user_id:         User identifier
        request_context: {
            "ip":                 Optional[str],
            "country":            Optional[str],    # ISO 3166-1 alpha-2
            "user_agent":         Optional[str],
            "device_fingerprint": Optional[str],
            "top_entities":       Optional[Set[str]], # client's known entity set
            "timestamp":          Optional[datetime]
        }

    Returns:
        {
            "trust_score": float (0.0-1.0),
            "risk_level":  str   ("low" | "medium" | "elevated" | "high"),
            "action":      str   ("allow" | "monitor" | "require_mfa" | "block"),
            "factors": {
                "ip_location": float,
                "device":      float,
                "behavioral":  float,
                "time_pattern":  None,   # TODO
                "api_behavior":  None,   # TODO
            }
        }
    """
    ip              = request_context.get("ip")
    country         = request_context.get("country")
    user_agent      = request_context.get("user_agent")
    device_fp       = request_context.get("device_fingerprint")
    top_entities: Optional[Set[str]] = request_context.get("top_entities")
    dt              = request_context.get("timestamp") or datetime.now(timezone.utc)

    # --- Signal 1: IP / Location (30%) ---
    ip_score = await _score_ip(db, user_id, ip, country)

    # --- Signal 2: Device Fingerprint (25%) ---
    device_score = await _score_device(db, user_id, device_fp, user_agent)

    # --- Signal 3: Behavioral fingerprint / Jaccard (20%) ---
    behavioral_score = await verify_fingerprint(db, user_id, top_entities)

    # --- Signal 4: Temporal Pattern (15%) ---
    time_score = await _score_time_pattern(db, user_id, dt)

    # --- Signal 5: API Behavior (10%) ---
    api_score = await _score_api_behavior(db, user_id)

    factors = {
        "ip_location":   round(ip_score, 3),
        "device":        round(device_score, 3),
        "behavioral":    round(behavioral_score, 3),
        "time_pattern":  round(time_score, 3),
        "api_behavior":  round(api_score, 3),
    }

    # Weighted ensemble
    trust_score = (
        ip_score         * WEIGHTS["ip_location"]
        + device_score   * WEIGHTS["device"]
        + behavioral_score * WEIGHTS["behavioral"]
        + time_score     * WEIGHTS["time_pattern"]
        + api_score      * WEIGHTS["api_behavior"]
    )
    trust_score = max(0.0, min(1.0, trust_score))

    # Determine risk level and recommended action
    if trust_score >= 0.80:
        risk_level, action = "low", "allow"
    elif trust_score >= 0.60:
        risk_level, action = "medium", "monitor"
    elif trust_score >= 0.40:
        risk_level, action = "elevated", "require_mfa"
    else:
        risk_level, action = "high", "block"

    return {
        "trust_score": round(trust_score, 3),
        "risk_level":  risk_level,
        "action":      action,
        "factors":     factors,
    }
