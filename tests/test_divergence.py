"""
Unit tests for divergence detection math.

Tests run without a database (pure function tests on continuity.py).
"""

import pytest
import numpy as np
from shadowwatch.invariant.state import InvariantState
from shadowwatch.invariant.continuity import (
    update_divergence,
    SHOCK_DISTANCE_THRESHOLD,
    CREEP_ACCUMULATION_THRESHOLD,
)


def _make_state(sample_count: int = 20, acc: float = 0.0, vel: float = 0.0, mode=None):
    """Create a test InvariantState."""
    import time
    state = InvariantState(
        user_id="test_user",
        created_at=time.time(),
        last_seen_at=time.time(),
    )
    state.sample_count = sample_count
    state.divergence_accumulated = acc
    state.divergence_velocity = vel
    state.divergence_mode = mode
    return state


class TestUpdateDivergence:

    def test_no_divergence_below_threshold(self):
        """Low distance → no divergence mode set."""
        state = _make_state()
        state = update_divergence(state, distance=0.1)
        assert state.divergence_mode is None

    def test_shock_classification(self):
        """A large single-step distance spike → shock mode."""
        state = _make_state()
        state = update_divergence(state, distance=SHOCK_DISTANCE_THRESHOLD + 1.0)
        assert state.divergence_mode == "shock"

    def test_creep_classification(self):
        """Sustained accumulation above threshold → creep mode."""
        state = _make_state()
        # Simulate many small anomalies accumulating
        state.divergence_accumulated = CREEP_ACCUMULATION_THRESHOLD + 0.1
        state.divergence_velocity = 0.1  # slow velocity = creep
        state = update_divergence(state, distance=0.8)
        assert state.divergence_mode == "creep"

    def test_fracture_classification(self):
        """Both shock and creep signals → fracture mode."""
        state = _make_state()
        state.divergence_accumulated = CREEP_ACCUMULATION_THRESHOLD + 0.2
        state.divergence_velocity = 0.1
        # Large distance spike (shock) + already accumulated (creep) = fracture
        state = update_divergence(state, distance=SHOCK_DISTANCE_THRESHOLD + 0.5)
        assert state.divergence_mode == "fracture"

    def test_recovery_clears_mode(self):
        """Normal behaviour after a divergence event → mode cleared."""
        state = _make_state(acc=0.1, mode="shock")
        # Simulate many normal observations → accumulation decays to < 0.2
        for _ in range(50):
            state.divergence_accumulated *= 0.95
        state = update_divergence(state, distance=0.1)
        # After decay below 0.2, mode should be cleared
        if state.divergence_accumulated < 0.2:
            assert state.divergence_mode is None

    def test_accumulated_never_exceeds_one(self):
        """Divergence accumulated is clamped to [0, 1]."""
        state = _make_state()
        for _ in range(100):
            state = update_divergence(state, distance=SHOCK_DISTANCE_THRESHOLD + 5.0)
        assert state.divergence_accumulated <= 1.0

    def test_accumulated_never_below_zero(self):
        """Divergence accumulated is clamped to >= 0."""
        state = _make_state(acc=0.01)
        for _ in range(50):
            state = update_divergence(state, distance=0.0)
        assert state.divergence_accumulated >= 0.0

    def test_early_samples_skipped(self):
        """Divergence is not calculated until sample_count >= 5."""
        state = _make_state(sample_count=4)
        original_mode = state.divergence_mode
        state = update_divergence(state, distance=SHOCK_DISTANCE_THRESHOLD + 10.0)
        # Should not classify — not enough samples
        assert state.divergence_mode == original_mode

    def test_velocity_updates(self):
        """Velocity should be non-zero after anomalous distance."""
        state = _make_state()
        initial_vel = state.divergence_velocity
        state = update_divergence(state, distance=SHOCK_DISTANCE_THRESHOLD + 1.0)
        # Velocity should have changed
        assert state.divergence_velocity != initial_vel

    def test_state_returned(self):
        """update_divergence should return the modified state."""
        state = _make_state()
        returned = update_divergence(state, distance=0.5)
        assert returned is state  # Modified in-place and returned
