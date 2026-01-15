"""
Invariant Module

Phase 1 Invariant tier - Temporal identity continuity and divergence detection.

This module implements behavioral baseline tracking and attack detection
for the Invariant license tier.
"""

from .state import InvariantState
from .continuity import (
    extract_features,
    update_baseline_welford,
    calculate_distance,
    temporal_decay,
    calculate_continuity_score,
    calculate_confidence,
)

__all__ = [
    "InvariantState",
    "extract_features",
    "update_baseline_welford",
    "calculate_distance",
    "temporal_decay",
    "calculate_continuity_score",
    "calculate_confidence",
]
