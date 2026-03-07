"""
Continuity Engine - Mathematical Functions

Implements behavioral continuity calculation using:
- Feature extraction (10-dimensional behavioral vector)
- Welford's online algorithm (baseline statistics)
- Variance-normalized distance
- Temporal decay
- Continuity scoring

Following Document 13 and Phase 1 Mathematical Spec exactly.
"""

import numpy as np
import math
from typing import List, Dict
from datetime import datetime
from collections import Counter

from .state import InvariantState


# =====================================================
# Constants
# =====================================================

# Temporal decay rates (λ)
LAMBDA_DAILY_ACTIVE = 0.0001    # 80-day half-life
LAMBDA_WEEKLY_ACTIVE = 0.001    # 8-day half-life  
LAMBDA_MONTHLY_ACTIVE = 0.01    # 17-hour half-life

# Confidence stabilization
CONFIDENCE_K = 50  # Samples for 63% confidence

# Distance epsilon
DISTANCE_EPSILON = 1e-6

# Human-readable feature labels for forensics
FEATURE_LABELS = {
    0: "session_duration",
    1: "inter_session_gap",
    2: "action_frequency",
    3: "tod_entropy",
    4: "action_diversity",
    5: "primary_action_ratio",
    6: "sequence_stability",
    7: "entity_focus_gini",
    8: "entity_churn",
    9: "entity_revisit_rate",
}


# =====================================================
# Feature Extraction
# =====================================================

def extract_features(events: List[dict]) -> np.ndarray:
    """
    Extract 10-dimensional behavioral feature vector
    
    Features:
    - 0-3: Temporal (session duration, gaps, frequency, time-of-day)
    - 4-6: Action (diversity, primary ratio, sequence stability)
    - 7-9: Entity (focus/Gini, churn, revisit rate)
    
    Args:
        events: List of activity events with:
            - timestamp: float (Unix timestamp)
            - action: str
            - entity_id: str
    
    Returns:
        x_t: np.ndarray of shape (10,)
    """
    features = np.zeros(10)
    
    if len(events) < 2:
        return features
    
    # === TEMPORAL FEATURES (0-3) ===
    
    # Feature 0: Average session duration (seconds)
    sessions = _split_into_sessions(events, gap_threshold=1800)  # 30 min gap
    if sessions:
        durations = [s[-1]['timestamp'] - s[0]['timestamp'] for s in sessions]
        features[0] = np.mean(durations) if durations else 0.0
    
    # Feature 1: Time between sessions (seconds)
    if len(sessions) > 1:
        session_starts = [s[0]['timestamp'] for s in sessions]
        gaps = [session_starts[i+1] - session_starts[i] 
                for i in range(len(session_starts)-1)]
        features[1] = np.mean(gaps) if gaps else 0.0
    
    # Feature 2: Action frequency (actions per minute)
    total_duration = events[-1]['timestamp'] - events[0]['timestamp']
    if total_duration > 0:
        features[2] = len(events) / (total_duration / 60)
    
    # Feature 3: Time-of-day entropy (normalized)
    hours = [datetime.fromtimestamp(e['timestamp']).hour for e in events]
    hour_counts = Counter(hours)
    total = len(events)
    if len(hour_counts) > 1:
        entropy = -sum((count/total) * math.log2(count/total) 
                       for count in hour_counts.values())
        features[3] = entropy / math.log2(24)  # Normalize to [0,1]
    
    # === ACTION FEATURES (4-6) ===
    
    actions = [e['action'] for e in events]
    action_counts = Counter(actions)
    
    # Feature 4: Action diversity (Shannon entropy)
    total = len(actions)
    n_actions = len(action_counts)
    if n_actions > 1:
        entropy = -sum((count/total) * math.log2(count/total) 
                       for count in action_counts.values())
        max_entropy = math.log2(n_actions)
        features[4] = entropy / max_entropy
    
    # Feature 5: Primary action ratio
    most_common_count = action_counts.most_common(1)[0][1]
    features[5] = most_common_count / len(actions)
    
    # Feature 6: Action sequence stability (bigram consistency)
    if len(actions) > 1:
        bigrams = [(actions[i], actions[i+1]) for i in range(len(actions)-1)]
        current_bigrams = set(bigrams)
        # Higher score = more repetitive (stable) sequences
        features[6] = 1.0 - (len(current_bigrams) / len(bigrams))
    
    # === ENTITY FEATURES (7-9) ===
    
    entities = [e['entity_id'] for e in events if e.get('entity_id')]
    
    if entities:
        entity_counts = Counter(entities)
        
        # Feature 7: Entity focus (Gini coefficient)
        sorted_counts = sorted(entity_counts.values())
        n = len(sorted_counts)
        index = sum((i+1) * count for i, count in enumerate(sorted_counts))
        features[7] = (2 * index) / (n * sum(sorted_counts)) - (n+1)/n
        
        # Feature 8: Entity churn (1 - diversity)
        n_unique = len(entity_counts)
        features[8] = 1.0 - (n_unique / len(entities))
        
        # Feature 9: Entity revisit rate
        revisited = sum(1 for count in entity_counts.values() if count > 1)
        features[9] = revisited / len(entity_counts) if len(entity_counts) > 0 else 0.0
    
    return features


def _split_into_sessions(events: List[dict], gap_threshold: int) -> List[List[dict]]:
    """
    Split events into sessions based on time gaps
    
    Args:
        events: List of events with timestamp field
        gap_threshold: Seconds of inactivity to split sessions
        
    Returns:
        List of session event lists
    """
    if not events:
        return []
    
    sessions = []
    current_session = [events[0]]
    
    for i in range(1, len(events)):
        gap = events[i]['timestamp'] - events[i-1]['timestamp']
        if gap > gap_threshold:
            sessions.append(current_session)
            current_session = [events[i]]
        else:
            current_session.append(events[i])
    
    sessions.append(current_session)
    return sessions


# =====================================================
# Baseline Update (Welford's Algorithm)
# =====================================================

def update_baseline_welford(
    state: InvariantState,
    x_t: np.ndarray
) -> InvariantState:
    """
    Update baseline using Welford's online algorithm
    
    Numerically stable incremental mean/variance calculation.
    
    Formulas:
        μₜ = μₜ₋₁ + (xₜ − μₜ₋₁) / n
        M2ₜ = M2ₜ₋₁ + (xₜ − μₜ₋₁)(xₜ − μₜ)
        σ²ₜ = M2ₜ / n
    
    Args:
        state: Current InvariantState
        x_t: New observation vector (10-dimensional)
    
    Returns:
        Updated InvariantState (modified in-place)
    """
    n = state.sample_count + 1
    
    # Update mean
    delta = x_t - state.baseline_vector
    state.baseline_vector = state.baseline_vector + delta / n
    
    # Update variance (M2 method)
    delta2 = x_t - state.baseline_vector
    state.baseline_variance = state.baseline_variance + delta * delta2
    
    # Increment count
    state.sample_count = n
    
    return state


def get_variance_from_m2(m2: np.ndarray, n: int) -> np.ndarray:
    """
    Convert M2 (sum of squared differences) to variance
    
    σ² = M2 / n  (we use population variance)
    
    Args:
        m2: M2 vector from Welford's algorithm
        n: Sample count
        
    Returns:
        Variance vector σ²
    """
    if n < 2:
        return np.zeros_like(m2)
    return m2 / n


# =====================================================
# Variance-Normalized Distance
# =====================================================

def calculate_distance(
    x_t: np.ndarray,
    mu: np.ndarray,
    sigma_squared: np.ndarray,
    epsilon: float = DISTANCE_EPSILON
) -> tuple[float, dict[str, float]]:
    """
    Calculate variance-normalized distance
    
    Formula:
        d_t = √(Σᵢ ((x_t[i] − μ[i])² / (σ²[i] + ε)))
    
    Args:
        x_t: Current feature vector
        mu: Baseline mean vector
        sigma_squared: Baseline variance vector
        epsilon: Small constant to prevent division by zero
    
    Returns:
        (total_distance, feature_deltas)
            - total_distance: Euclidean distance of normalized deltas
            - feature_deltas: {label: normalized_distance} for each feature
    """
    variance_norm = sigma_squared + epsilon
    squared_diff = (x_t - mu) ** 2
    normalized_squared_diff = squared_diff / variance_norm
    
    feature_distances = np.sqrt(normalized_squared_diff)
    total_distance = np.sqrt(np.sum(normalized_squared_diff))
    
    # Create forensic dictionary
    deltas = {
        FEATURE_LABELS[i]: float(feature_distances[i])
        for i in range(len(feature_distances))
    }
    
    return float(total_distance), deltas


# =====================================================
# Temporal Decay
# =====================================================

def temporal_decay(
    delta_t: float,
    lambda_param: float = LAMBDA_DAILY_ACTIVE
) -> float:
    """
    Exponential decay based on time since last activity
    
    Formula:
        decay(Δt) = e^(-λΔt)
    
    Args:
        delta_t: Time since last activity (seconds)
        lambda_param: Decay rate
            - 0.0001 → ~80 day half-life (recommended)
            - 0.001  → ~8 day half-life
            - 0.01   → ~17 hour half-life
    
    Returns:
        decay: float ∈ (0, 1]
    """
    decay = math.exp(-lambda_param * delta_t)
    return decay


def half_life_from_lambda(lambda_param: float) -> float:
    """
    Calculate half-life from decay constant
    
    t_{1/2} = ln(2) / λ
    
    Args:
        lambda_param: Decay constant
        
    Returns:
        Half-life in seconds
    """
    return math.log(2) / lambda_param


# =====================================================
# Continuity Score
# =====================================================

def calculate_continuity_score(
    distance: float,
    delta_t: float,
    lambda_param: float = LAMBDA_DAILY_ACTIVE
) -> float:
    """
    Calculate continuity score
    
    Formula:
        C_t = decay(Δt) × e^(-d_t)
    
    Properties:
    - C_t ∈ (0, 1]
    - Monotonic in time (without reinforcement)
    - Monotonic in distance
    - Cannot spike instantly
    
    Args:
        distance: Behavioral distance d_t
        delta_t: Time since last activity (seconds)
        lambda_param: Temporal decay rate
    
    Returns:
        score: float ∈ [0, 1]
    """
    # Temporal decay component
    decay = temporal_decay(delta_t, lambda_param)
    
    # Behavioral match component
    behavior_match = math.exp(-distance)
    
    # Combined score
    score = decay * behavior_match
    
    # Clamp to valid range
    return np.clip(score, 0.0, 1.0)


# =====================================================
# Confidence Calculation
# =====================================================

def calculate_confidence(
    sample_count: int,
    k: int = CONFIDENCE_K
) -> float:
    """
    Calculate confidence in continuity score

    Formula:
        confidence = 1 − e^(-n / k)

    Grows asymptotically to 1.0 as sample count increases.

    Confidence levels:
        n = 0   → 0.00  (no data)
        n = 10  → 0.18  (very low)
        n = 25  → 0.39  (low)
        n = 50  → 0.63  (moderate)
        n = 100 → 0.86  (high)
        n = 150 → 0.95  (very high)

    Args:
        sample_count: Number of observations
        k: Stabilization constant (samples for ~63% confidence)

    Returns:
        confidence: float ∈ [0, 1]
    """
    confidence = 1.0 - math.exp(-sample_count / k)
    return np.clip(confidence, 0.0, 1.0)


# =====================================================
# Divergence Detection
# =====================================================

# Thresholds for divergence mode classification
SHOCK_DISTANCE_THRESHOLD = 2.0   # Single-step spike indicating fast takeover
CREEP_ACCUMULATION_THRESHOLD = 1.0  # Slow accumulation indicating gradual drift
DIVERGENCE_DECAY = 0.95          # Decay factor when behavior recovers
VELOCITY_SMOOTHING = 0.3         # EMA weight for velocity smoothing


def update_divergence(
    state: InvariantState,
    distance: float,
) -> InvariantState:
    """
    Update divergence accumulation and classify the attack mode.

    Divergence is a ratcheting signal — it accumulates when the actor
    behaves anomalously and decays slowly when behavior normalises.

    Modes:
        shock    — distance spiked sharply in a single step (fast ATO)
        creep    — slow, continuous accumulation (gradual ATO / account drift)
        fracture — both shock and creep signals present (mixed/partial control)
        None     — no significant divergence

    Args:
        state:    Current InvariantState (modified in-place)
        distance: Current behavioral distance d_t

    Returns:
        Updated InvariantState
    """
    # Need at least a few samples before declaring divergence
    if state.sample_count < 5:
        return state

    # Track previous accumulated divergence for velocity calculation
    prev_accumulated = state.divergence_accumulated

    # Accumulate or decay depending on current distance relative to threshold
    normalized_distance = distance / max(state.sample_count ** 0.5, 1.0)

    if normalized_distance > 0.5:
        # Anomalous — ratchet up
        state.divergence_accumulated = min(
            1.0,
            state.divergence_accumulated + normalized_distance * 0.1
        )
    else:
        # Normal behaviour — slowly decay accumulated divergence
        state.divergence_accumulated = max(
            0.0,
            state.divergence_accumulated * DIVERGENCE_DECAY
        )

    # Update velocity (exponential moving average of accumulation rate)
    delta = state.divergence_accumulated - prev_accumulated
    state.divergence_velocity = (
        VELOCITY_SMOOTHING * delta
        + (1 - VELOCITY_SMOOTHING) * state.divergence_velocity
    )

    # Classify divergence mode
    is_shock = distance > SHOCK_DISTANCE_THRESHOLD
    is_creep = (
        state.divergence_accumulated >= CREEP_ACCUMULATION_THRESHOLD
        and abs(state.divergence_velocity) < 0.5
    )

    if is_shock and is_creep:
        state.divergence_mode = "fracture"
    elif is_shock:
        state.divergence_mode = "shock"
    elif is_creep:
        state.divergence_mode = "creep"
    elif state.divergence_accumulated < 0.2:
        # Sufficiently recovered — clear the mode
        state.divergence_mode = None

    return state


def reset_divergence_if_recovered(
    state: InvariantState,
    consecutive_high_score_steps: int = 5
) -> InvariantState:
    """
    Decay divergence if the user has stabilized.
    
    If the continuity score is high for multiple steps, it suggests the 
    'new' behavior is now the stable baseline for this actor.
    
    Args:
        state: InvariantState
        consecutive_high_score_steps: Not implemented tracking here, 
                                      using simpler score-based decay.
    """
    if state.continuity_score > 0.8:
        state.divergence_accumulated *= 0.8
        if state.divergence_accumulated < 0.1:
            state.divergence_mode = None
            
    return state
