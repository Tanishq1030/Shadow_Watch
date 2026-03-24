"""
Unit tests for the BehavioralAnomalyScorer localized model.

All tests run without a real database (AsyncMock for DB sessions).
"""

import math
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from shadowwatch.core.behavioral import (
    BehavioralAnomalyScorer,
    score_behavioral_anomaly,
    _kl_divergence,
    _kl_to_score,
    _zscore_to_score,
    MIN_HISTORY_EVENTS,
    SIGNAL_WEIGHTS,
)


# ---------------------------------------------------------------------------
# Helper: build lists of fake events
# ---------------------------------------------------------------------------

def _make_events(action_types, symbols=None, base_time=None, interval_seconds=60):
    """Build a list of event dicts."""
    if base_time is None:
        base_time = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
    if symbols is None:
        symbols = ["AAPL"] * len(action_types)
    events = []
    for i, (action, symbol) in enumerate(zip(action_types, symbols)):
        events.append({
            "action_type": action,
            "symbol": symbol,
            "occurred_at": base_time + timedelta(seconds=i * interval_seconds),
        })
    return events


def _make_db_with_history(history_events):
    """Return an AsyncMock DB that serves the given history rows."""
    mock_db = AsyncMock()

    def _make_row(ev):
        row = MagicMock()
        row.action_type = ev["action_type"]
        row.symbol = ev["symbol"]
        row.occurred_at = ev["occurred_at"]
        return row

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [_make_row(e) for e in history_events]
    mock_db.execute = AsyncMock(return_value=mock_result)
    return mock_db


# ---------------------------------------------------------------------------
# Pure helper function tests
# ---------------------------------------------------------------------------

class TestKLDivergence:

    def test_identical_distributions(self):
        p = {"view": 0.5, "search": 0.5}
        kl = _kl_divergence(p, p)
        assert kl < 1e-6

    def test_divergent_distributions(self):
        p = {"trade": 1.0}  # all trades
        q = {"view": 1.0}   # all views
        kl = _kl_divergence(p, q)
        assert kl > 1.0  # significant divergence

    def test_zero_probability_handled(self):
        p = {"view": 1.0}
        q = {}  # empty
        # Should not raise (Laplace smoothing)
        kl = _kl_divergence(p, q)
        assert kl >= 0.0

    def test_symmetry_not_required(self):
        p = {"view": 0.8, "trade": 0.2}
        q = {"view": 0.2, "trade": 0.8}
        kl_pq = _kl_divergence(p, q)
        kl_qp = _kl_divergence(q, p)
        # Both are valid (non-negative) KL values; asymmetry is expected
        assert kl_pq >= 0.0
        assert kl_qp >= 0.0


class TestKLToScore:

    def test_zero_kl_gives_one(self):
        assert abs(_kl_to_score(0.0) - 1.0) < 1e-9

    def test_large_kl_near_zero(self):
        assert _kl_to_score(10.0) < 0.01

    def test_monotone_decreasing(self):
        scores = [_kl_to_score(k) for k in [0.0, 0.5, 1.0, 2.0, 5.0]]
        for a, b in zip(scores, scores[1:]):
            assert a > b


class TestZScoreToScore:

    def test_zero_zscore_gives_one(self):
        assert abs(_zscore_to_score(0.0) - 1.0) < 1e-9

    def test_large_zscore_low_score(self):
        assert _zscore_to_score(3.0) < 0.15

    def test_negative_treated_as_abs(self):
        assert abs(_zscore_to_score(-2.0) - _zscore_to_score(2.0)) < 1e-9


# ---------------------------------------------------------------------------
# BehavioralAnomalyScorer sub-signal tests (static methods)
# ---------------------------------------------------------------------------

class TestActionDistributionScorer:

    def test_identical_distribution_score_one(self):
        history = _make_events(["view"] * 5 + ["search"] * 5)
        session = _make_events(["view"] * 3 + ["search"] * 3)
        score = BehavioralAnomalyScorer._score_action_distribution(history, session)
        assert score > 0.95

    def test_completely_different_action_type(self):
        history = _make_events(["view"] * 20)
        session = _make_events(["trade"] * 5)
        score = BehavioralAnomalyScorer._score_action_distribution(history, session)
        assert score < 0.5

    def test_score_range(self):
        for actions in [["view", "trade"], ["search"] * 3, ["watchlist_add", "alert_set"]]:
            history = _make_events(actions * 5)
            session = _make_events(actions[:1] * 3)
            score = BehavioralAnomalyScorer._score_action_distribution(history, session)
            assert 0.0 <= score <= 1.0


class TestVelocityScorer:

    def test_normal_velocity_high_score(self):
        # History: 10 events per hour (steady)
        base = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
        history = []
        for h in range(5):  # 5 hours
            for m in range(10):  # 10 events each hour
                history.append({
                    "action_type": "view",
                    "symbol": "AAPL",
                    "occurred_at": base + timedelta(hours=h, minutes=m * 6),
                })
        # Session velocity == historical mean → z ≈ 0 → high score
        session = _make_events(["view"] * 10, interval_seconds=360)  # 10 in 1 hour
        score = BehavioralAnomalyScorer._score_velocity(history, session, window_hours=1.0)
        assert score > 0.7

    def test_velocity_spike_low_score(self):
        # History: 2 events per hour
        base = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
        history = []
        for h in range(10):
            for m in [0, 30]:
                history.append({
                    "action_type": "view",
                    "symbol": "AAPL",
                    "occurred_at": base + timedelta(hours=h, minutes=m),
                })
        # Session: 60 events in 1 hour → extreme spike
        session = _make_events(["view"] * 60, interval_seconds=60)
        score = BehavioralAnomalyScorer._score_velocity(history, session, window_hours=1.0)
        assert score < 0.5

    def test_empty_history_returns_one(self):
        score = BehavioralAnomalyScorer._score_velocity([], [], window_hours=1.0)
        assert score == 1.0


class TestEntityNoveltyScorer:

    def test_all_known_entities(self):
        history = _make_events(["view"] * 5, symbols=["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"])
        session = _make_events(["view"] * 3, symbols=["AAPL", "GOOGL", "MSFT"])
        score = BehavioralAnomalyScorer._score_entity_novelty(history, session)
        assert score == 1.0

    def test_all_novel_entities(self):
        history = _make_events(["view"] * 3, symbols=["AAPL", "GOOGL", "MSFT"])
        session = _make_events(["view"] * 3, symbols=["NFLX", "NVDA", "AMD"])
        score = BehavioralAnomalyScorer._score_entity_novelty(history, session)
        assert score == 0.0

    def test_partial_novelty(self):
        history = _make_events(["view"] * 2, symbols=["AAPL", "GOOGL"])
        session = _make_events(["view"] * 4, symbols=["AAPL", "GOOGL", "TSLA", "AMZN"])
        score = BehavioralAnomalyScorer._score_entity_novelty(history, session)
        assert abs(score - 0.5) < 1e-9

    def test_no_session_returns_one(self):
        history = _make_events(["view"] * 3, symbols=["AAPL", "GOOGL", "MSFT"])
        score = BehavioralAnomalyScorer._score_entity_novelty(history, session=[])
        assert score == 1.0

    def test_no_history_lenient(self):
        session = _make_events(["view"] * 3, symbols=["AAPL", "GOOGL", "MSFT"])
        score = BehavioralAnomalyScorer._score_entity_novelty([], session)
        assert score == 0.75


# ---------------------------------------------------------------------------
# BehavioralAnomalyScorer.score() integration tests (mocked DB)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestBehavioralAnomalyScorerIntegration:

    async def test_insufficient_history_returns_neutral(self):
        """Fewer than MIN_HISTORY_EVENTS → lenient score (0.75)."""
        history = _make_events(["view"] * (MIN_HISTORY_EVENTS - 1))
        db = _make_db_with_history(history)
        scorer = BehavioralAnomalyScorer(db, user_id=1)
        score = await scorer.score(session_events=[_make_events(["view"])[0]])
        assert score == 0.75

    async def test_normal_session_high_score(self):
        """Session that perfectly mirrors history should score high."""
        history = _make_events(
            ["view"] * 8 + ["search"] * 4 + ["trade"] * 1,
            symbols=["AAPL"] * 8 + ["GOOGL"] * 4 + ["MSFT"] * 1,
        )
        # Session repeats the same pattern and symbols
        session = _make_events(
            ["view"] * 3 + ["search"] * 2,
            symbols=["AAPL"] * 3 + ["GOOGL"] * 2,
        )
        db = _make_db_with_history(history)
        scorer = BehavioralAnomalyScorer(db, user_id=1)
        score = await scorer.score(session_events=session)
        assert score > 0.65

    async def test_anomalous_session_low_score(self):
        """Session with entirely different action types and symbols → low score."""
        history = _make_events(
            ["view"] * 15,
            symbols=["AAPL"] * 15,
        )
        # Anomalous: all trades, all unfamiliar symbols
        session = _make_events(
            ["trade"] * 5,
            symbols=["NFLX", "NVDA", "AMD", "META", "SNAP"],
        )
        db = _make_db_with_history(history)
        scorer = BehavioralAnomalyScorer(db, user_id=1)
        score = await scorer.score(session_events=session)
        assert score < 0.65

    async def test_score_always_in_range(self):
        """Score must always be in [0.0, 1.0]."""
        for n_hist in [MIN_HISTORY_EVENTS, MIN_HISTORY_EVENTS * 2]:
            history = _make_events(["view"] * n_hist)
            for session_actions in [["trade"] * 3, ["view"] * 3, []]:
                session = _make_events(session_actions) if session_actions else []
                db = _make_db_with_history(history)
                scorer = BehavioralAnomalyScorer(db, user_id=1)
                score = await scorer.score(session_events=session)
                assert 0.0 <= score <= 1.0, f"Out-of-range score {score}"

    async def test_no_session_events_uses_db(self):
        """When session_events=None, scorer fetches from DB (returns lenient)."""
        # Both history and recent-session queries return the same mock
        history = _make_events(["view"] * (MIN_HISTORY_EVENTS - 1))
        db = _make_db_with_history(history)
        scorer = BehavioralAnomalyScorer(db, user_id=1)
        # With insufficient history, score should be 0.75 regardless
        score = await scorer.score(session_events=None)
        assert score == 0.75


# ---------------------------------------------------------------------------
# score_behavioral_anomaly convenience function
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestScoreBehavioralAnomalyFunction:

    async def test_returns_float_in_range(self):
        history = _make_events(["view"] * (MIN_HISTORY_EVENTS - 1))
        db = _make_db_with_history(history)
        result = await score_behavioral_anomaly(db, user_id=1)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    async def test_passes_session_events(self):
        history = _make_events(["view"] * (MIN_HISTORY_EVENTS - 1))
        session = _make_events(["trade"] * 3)
        db = _make_db_with_history(history)
        result = await score_behavioral_anomaly(db, user_id=1, session_events=session)
        assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# trust_score.py integration — _score_behavioral helper
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestScoreBehavioralInTrustScore:

    @patch("shadowwatch.core.trust_score.score_behavioral_anomaly")
    @patch("shadowwatch.core.trust_score.verify_fingerprint")
    async def test_behavioral_averages_jaccard_and_anomaly(self, mock_jaccard, mock_anomaly):
        """_score_behavioral returns the mean of Jaccard and anomaly scores."""
        from shadowwatch.core.trust_score import _score_behavioral

        mock_jaccard.return_value = 0.8
        mock_anomaly.return_value = 0.4

        db = AsyncMock()
        result = await _score_behavioral(db, user_id=1, top_entities={"AAPL"}, session_events=[])
        assert abs(result - 0.6) < 1e-9

    @patch("shadowwatch.core.trust_score.score_behavioral_anomaly")
    @patch("shadowwatch.core.trust_score.verify_fingerprint")
    async def test_calculate_trust_score_includes_session_events(self, mock_jaccard, mock_anomaly):
        """calculate_trust_score passes session_events through to behavioral scorer."""
        from shadowwatch.core.trust_score import (
            calculate_trust_score,
            _score_ip,
            _score_device,
            _score_time_pattern,
            _score_api_behavior,
        )

        mock_jaccard.return_value = 1.0
        mock_anomaly.return_value = 1.0

        session = [{"action_type": "view", "symbol": "AAPL",
                    "occurred_at": datetime(2024, 1, 1, tzinfo=timezone.utc)}]

        with (
            patch("shadowwatch.core.trust_score._score_ip", return_value=1.0),
            patch("shadowwatch.core.trust_score._score_device", return_value=1.0),
            patch("shadowwatch.core.trust_score._score_time_pattern", return_value=1.0),
            patch("shadowwatch.core.trust_score._score_api_behavior", return_value=1.0),
        ):
            db = AsyncMock()
            result = await calculate_trust_score(
                db,
                user_id=1,
                request_context={"session_events": session, "top_entities": {"AAPL"}},
            )

        assert result["trust_score"] == 1.0
        assert result["factors"]["behavioral"] == 1.0
        # anomaly scorer was called with the session_events we passed
        mock_anomaly.assert_called_once()
        args = mock_anomaly.call_args[0]
        kw = mock_anomaly.call_args[1]
        forwarded = args[2] if len(args) > 2 else kw.get("session_events")
        assert forwarded == session
