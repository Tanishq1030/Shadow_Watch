"""
Continuity Integration Module

Provides calculate_continuity and detect_divergence implementations.
Separated for code organization and to avoid bloating main.py.
"""

from typing import Dict, Optional, List
import time
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from shadowwatch.invariant import (
    InvariantState,
    extract_features,
    update_baseline_welford,
    calculate_distance,
    calculate_continuity_score,
    calculate_confidence,
)
from shadowwatch.invariant.continuity import update_divergence


async def _load_invariant_state(
    db_session: AsyncSession,
    subject_id: str
):
    """
    Load existing InvariantState from DB or create a fresh one.

    Returns (state, exists) where exists=True means a row was found.
    """
    from sqlalchemy import text as sa_text
    result = await db_session.execute(
        sa_text("SELECT * FROM invariant_state WHERE user_id = :user_id"),
        {"user_id": subject_id}
    )
    row = result.fetchone()

    if row:
        state = InvariantState.from_dict(dict(row._mapping))
        return state, True
    else:
        state = InvariantState(
            user_id=subject_id,
            created_at=time.time(),
            last_seen_at=time.time()
        )
        return state, False


async def _fetch_recent_events(
    db_session: AsyncSession,
    subject_id: str,
    limit: int = 100
) -> List[dict]:
    """
    Fetch recent activity events for a user via ORM.

    Maps UserActivityEvent columns → the feature extractor's expected keys:
        occurred_at  → timestamp (float)
        action_type  → action
        symbol       → entity_id

    NOTE: subject_id may be passed as a string (e.g. "123") even though
    the activity model stores user_id as integer. We cast defensively.
    """
    from shadowwatch.models.activity import UserActivityEvent

    # Normalize subject_id to int for the activity table lookup
    try:
        uid_int = int(subject_id)
    except (ValueError, TypeError):
        # Non-numeric subject_id — no activity events exist yet
        return []

    stmt = (
        select(UserActivityEvent)
        .where(UserActivityEvent.user_id == uid_int)
        .order_by(desc(UserActivityEvent.occurred_at))
        .limit(limit)
    )
    result = await db_session.execute(stmt)
    rows = result.scalars().all()

    events = [
        {
            "timestamp": row.occurred_at.timestamp(),
            "action": row.action_type,
            "entity_id": row.symbol,
        }
        for row in rows
    ]
    # Reverse from DESC → chronological order
    events.reverse()
    return events


async def _persist_invariant_state(
    db_session: AsyncSession,
    state: InvariantState,
    existed: bool,
    distance: float,
) -> None:
    """Upsert invariant_state and append to continuity_history."""
    from sqlalchemy import text as sa_text
    import json

    state_params = {
        "user_id": state.user_id,
        "baseline_vector": json.dumps(state.baseline_vector.tolist()),
        "baseline_variance": json.dumps(state.baseline_variance.tolist()),
        "sample_count": state.sample_count,
        "continuity_score": float(state.continuity_score),
        "continuity_confidence": float(state.continuity_confidence),
        "divergence_accumulated": float(state.divergence_accumulated),
        "divergence_velocity": float(state.divergence_velocity),
        "divergence_mode": state.divergence_mode,
        "last_seen_at": state.last_seen_at,
    }

    if existed:
        await db_session.execute(
            sa_text("""
            UPDATE invariant_state
            SET baseline_vector        = :baseline_vector,
                baseline_variance      = :baseline_variance,
                sample_count           = :sample_count,
                continuity_score       = :continuity_score,
                continuity_confidence  = :continuity_confidence,
                divergence_accumulated = :divergence_accumulated,
                divergence_velocity    = :divergence_velocity,
                divergence_mode        = :divergence_mode,
                last_seen_at           = :last_seen_at
            WHERE user_id = :user_id
            """),
            state_params,
        )
    else:
        await db_session.execute(
            sa_text("""
            INSERT INTO invariant_state (
                user_id, created_at, last_seen_at,
                baseline_vector, baseline_variance, sample_count,
                continuity_score, continuity_confidence,
                divergence_accumulated, divergence_velocity, divergence_mode
            ) VALUES (
                :user_id, :created_at, :last_seen_at,
                :baseline_vector, :baseline_variance, :sample_count,
                :continuity_score, :continuity_confidence,
                :divergence_accumulated, :divergence_velocity, :divergence_mode
            )
            """),
            {**state_params, "created_at": state.created_at},
        )

    # Append continuity_history row
    await db_session.execute(
        sa_text("""
        INSERT INTO continuity_history (
            user_id, continuity_score, confidence,
            distance, decay_factor, sample_count
        ) VALUES (
            :user_id, :continuity_score, :confidence,
            :distance, :decay_factor, :sample_count
        )
        """),
        {
            "user_id": state.user_id,
            "continuity_score": float(state.continuity_score),
            "confidence": float(state.continuity_confidence),
            "distance": float(distance),
            "decay_factor": 1.0,
            "sample_count": state.sample_count,
        },
    )


async def _log_divergence_event(
    db_session: AsyncSession,
    state: InvariantState,
    distance: float,
    deltas: dict[str, float],
) -> None:
    """Log a divergence event to divergence_events table for forensic review."""
    from sqlalchemy import text as sa_text
    import json

    if not state.divergence_mode:
        return

    await db_session.execute(
        sa_text("""
        INSERT INTO divergence_events (
            user_id, mode, magnitude, velocity, confidence, feature_deltas
        ) VALUES (
            :user_id, :mode, :magnitude, :velocity, :confidence, :feature_deltas
        )
        """),
        {
            "user_id": state.user_id,
            "mode": state.divergence_mode,
            "magnitude": float(min(state.divergence_accumulated, 1.0)),
            "velocity": float(state.divergence_velocity),
            "confidence": float(state.continuity_confidence),
            "feature_deltas": json.dumps(deltas),
        },
    )


async def calculate_continuity_impl(
    db_session: AsyncSession,
    subject_id: str,
    context: Optional[Dict] = None,
) -> Dict:
    """
    Calculate temporal actor persistence (ATO detection core).

    Args:
        db_session: SQLAlchemy async session
        subject_id: User/subject identifier (may be str or int)
        context:    Optional contextual signals (IP, device, location)

    Returns::
        {
            "score":        float  ∈ [0, 1]   (1 = same actor confirmed)
            "confidence":   float  ∈ [0, 1]   (grows with sample count)
            "state":        str    learning | stable | drifting | diverging
            "sample_count": int
            "distance":     float              (behavioral distance d_t)
        }
    """
    # Normalize subject_id to string for invariant state storage
    subject_id = str(subject_id)

    # 1. Load or create InvariantState
    state, existed = await _load_invariant_state(db_session, subject_id)

    # 2. Fetch recent events via ORM (correct table + column names)
    events = await _fetch_recent_events(db_session, subject_id)

    if len(events) < 2:
        return {
            "score": 1.0,
            "confidence": 0.0,
            "state": "learning",
            "sample_count": len(events),
            "distance": 0.0,
        }

    # 3. Extract 10-dimensional behavioral feature vector
    x_t = extract_features(events)

    # 4. Calculate variance-normalized distance (if baseline exists)
    if state.sample_count > 0:
        from shadowwatch.invariant.continuity import get_variance_from_m2
        variance = get_variance_from_m2(state.baseline_variance, state.sample_count)
        distance, deltas = calculate_distance(x_t, state.baseline_vector, variance)
    else:
        distance, deltas = 0.0, {}

    # 5. Update baseline (Welford's online algorithm)
    state = update_baseline_welford(state, x_t)

    # 6. Calculate continuity score with temporal decay
    current_time = time.time()
    delta_t = max(current_time - state.last_seen_at, 0.0)
    continuity_score = calculate_continuity_score(distance, delta_t)

    # 7. Calculate confidence (grows asymptotically with sample count)
    confidence = calculate_confidence(state.sample_count)

    # 8. Update divergence signals
    state = update_divergence(state, distance)

    # 9. Update state fields
    state.continuity_score = continuity_score
    state.continuity_confidence = confidence
    state.last_seen_at = current_time

    # 10. Classify behavioral state
    if state.sample_count < 10:
        classification = "learning"
    elif continuity_score > 0.8:
        classification = "stable"
    elif continuity_score > 0.5:
        classification = "drifting"
    else:
        classification = "diverging"

    # 11. Persist state + continuity history
    await _persist_invariant_state(db_session, state, existed, distance)

    # 12. Log divergence event when adversarial signal is present
    if classification == "diverging" and state.divergence_mode:
        await _log_divergence_event(db_session, state, distance, deltas)

    await db_session.commit()

    return {
        "score": float(state.continuity_score),
        "confidence": float(state.continuity_confidence),
        "state": classification,
        "sample_count": state.sample_count,
        "distance": float(distance),
    }


async def detect_divergence_impl(
    db_session: AsyncSession,
    subject_id: str,
    window_hours: int = 24,
) -> Dict:
    """
    Detect behavioral divergence over a time window.

    Reads continuity_history for the last `window_hours` hours and
    derives the current divergence state from the most recent
    InvariantState row.

    Args:
        db_session:   SQLAlchemy async session
        subject_id:   User identifier
        window_hours: How many hours of history to inspect (default: 24)

    Returns::
        {
            "magnitude":  float  ∈ [0, 1]  (accumulated divergence)
            "velocity":   float             (rate of change)
            "mode":       str    shock | creep | fracture | none
            "confidence": float  ∈ [0, 1]
        }
    """
    from sqlalchemy import text as sa_text

    subject_id = str(subject_id)

    # Load current invariant state
    state, existed = await _load_invariant_state(db_session, subject_id)

    if not existed or state.sample_count < 2:
        return {
            "magnitude": 0.0,
            "velocity": 0.0,
            "mode": "none",
            "confidence": 0.0,
        }

    return {
        "magnitude": float(min(state.divergence_accumulated, 1.0)),
        "velocity": float(state.divergence_velocity),
        "mode": state.divergence_mode or "none",
        "confidence": float(state.continuity_confidence),
    }
