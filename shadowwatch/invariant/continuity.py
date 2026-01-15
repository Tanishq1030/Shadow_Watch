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
) -> float:
    """
    Calculate variance-normalized distance
    
    Formula:
        d_t = √(Σᵢ ((x_t[i] − μ[i])² / (σ²[i] + ε)))
    
    Similar to Mahalanobis distance but assumes diagonal covariance.
    
    Args:
        x_t: Current feature vector
        mu: Baseline mean vector
        sigma_squared: Baseline variance vector
        epsilon: Small constant to prevent division by zero
    
    Returns:
        d_t: Distance (scalar, ≥ 0)
    """
    # Prevent division by zero
    variance_norm = sigma_squared + epsilon
    
    # Squared difference
    squared_diff = (x_t - mu) ** 2
    
    # Normalize by variance and sum
    normalized_squared_diff = squared_diff / variance_norm
    
    # Take square root
    distance = np.sqrt(np.sum(normalized_squared_diff))
    
    return float(distance)


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
