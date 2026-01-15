"""
Continuity Integration Module

Provides calculate_continuity implementation for ShadowWatch main class.
Separated for code organization and to avoid bloating main.py.
"""

from typing import Dict, Optional
import time

from shadowwatch.invariant import (
    InvariantState,
    extract_features,
    update_baseline_welford,
    calculate_distance,
    calculate_continuity_score,
    calculate_confidence,
)


async def calculate_continuity_impl(
    db_session,
    subject_id: str,
    context: Optional[Dict] = None
) -> Dict:
    """
    Calculate temporal actor persistence
    
    Implementation of calculate_continuity() for Invariant tier.
    
    Args:
        db_session: Database session
        subject_id: User/subject identifier
        context: Optional context dict
        
    Returns:
        Result dict with score, confidence, state, sample_count, distance
    """
    # 1. Load or create InvariantState
    result = await db_session.execute(
        "SELECT * FROM invariant_state WHERE user_id = :user_id",
        {"user_id": subject_id}
    )
    row = result.fetchone()
    
    if row:
        # Load existing state
        state = InvariantState.from_dict(dict(row._mapping))
    else:
        # Create new state
        state = InvariantState(
            user_id=subject_id,
            created_at=time.time(),
            last_seen_at=time.time()
        )
    
    # 2. Fetch recent events (last 100 for feature extraction)
    events_result = await db_session.execute(
        """
        SELECT timestamp, action, entity_id
        FROM activities
        WHERE user_id = :user_id
        ORDER BY timestamp DESC
        LIMIT 100
        """,
        {"user_id": subject_id}
    )
    events = [
        {
            "timestamp": float(row.timestamp),
            "action": row.action,
            "entity_id": row.entity_id
        }
        for row in events_result.fetchall()
    ]
    
    if len(events) < 2:
        # Not enough data
        return {
            "score": 1.0,
            "confidence": 0.0,
            "state": "learning",
            "sample_count": len(events),
            "distance": 0.0
        }
    
    # Reverse to chronological order
    events.reverse()
    
    # 3. Extract features
    x_t = extract_features(events)
    
    # 4. Calculate distance (if baseline exists)
    if state.sample_count > 0:
        variance = state.baseline_variance / state.sample_count if state.sample_count > 1 else state.baseline_variance
        distance = calculate_distance(x_t, state.baseline_vector, variance)
    else:
        distance = 0.0
    
    # 5. Update baseline with new observation (Welford's algorithm)
    state = update_baseline_welford(state, x_t)
    
    # 6. Calculate continuity score
    current_time = time.time()
    delta_t = current_time - state.last_seen_at
    continuity_score = calculate_continuity_score(distance, delta_t)
    
    # 7. Calculate confidence
    confidence = calculate_confidence(state.sample_count)
    
    # 8. Update state
    state.continuity_score = continuity_score
    state.continuity_confidence = confidence
    state.last_seen_at = current_time
    
    # 9. Classify state
    if state.sample_count < 10:
        classification = "learning"
    elif continuity_score > 0.8:
        classification = "stable"
    elif continuity_score > 0.5:
        classification = "drifting"
    else:
        classification = "diverging"
    
    # 10. Persist state to database
    if row:
        # Update existing
        await db_session.execute(
            """
            UPDATE invariant_state
            SET baseline_vector = :baseline_vector,
                baseline_variance = :baseline_variance,
                sample_count = :sample_count,
                continuity_score = :continuity_score,
                continuity_confidence = :continuity_confidence,
                last_seen_at = :last_seen_at
            WHERE user_id = :user_id
            """,
            {
                "user_id": subject_id,
                "baseline_vector": state.baseline_vector.tolist(),
                "baseline_variance": state.baseline_variance.tolist(),
                "sample_count": state.sample_count,
                "continuity_score": state.continuity_score,
                "continuity_confidence": state.continuity_confidence,
                "last_seen_at": state.last_seen_at
            }
        )
    else:
        # Insert new
        await db_session.execute(
            """
            INSERT INTO invariant_state (
                user_id, created_at, last_seen_at,
                baseline_vector, baseline_variance, sample_count,
                continuity_score, continuity_confidence
            ) VALUES (
                :user_id, :created_at, :last_seen_at,
                :baseline_vector, :baseline_variance, :sample_count,
                :continuity_score, :continuity_confidence
            )
            """,
            {
                "user_id": subject_id,
                "created_at": state.created_at,
                "last_seen_at": state.last_seen_at,
                "baseline_vector": state.baseline_vector.tolist(),
                "baseline_variance": state.baseline_variance.tolist(),
                "sample_count": state.sample_count,
                "continuity_score": state.continuity_score,
                "continuity_confidence": state.continuity_confidence
            }
        )
    
    # 11. Log to continuity_history
    await db_session.execute(
        """
        INSERT INTO continuity_history (
            user_id, continuity_score, confidence,
            distance, decay_factor, sample_count
        ) VALUES (
            :user_id, :continuity_score, :confidence,
            :distance, :decay_factor, :sample_count
        )
        """,
        {
            "user_id": subject_id,
            "continuity_score": state.continuity_score,
            "confidence": state.continuity_confidence,
            "distance": distance,
            "decay_factor": 1.0,  # Simplified for now
            "sample_count": state.sample_count
        }
    )
    
    await db_session.commit()
    
    # 12. Return result
    return {
        "score": float(state.continuity_score),
        "confidence": float(state.continuity_confidence),
        "state": classification,
        "sample_count": state.sample_count,
        "distance": float(distance)
    }
