"""
Behavioral Anomaly Scorer — Localized Per-User Model

Answers the question: does the *pattern* of interactions in this session
match what we historically expect from this user?

Unlike pure telemetry heuristics (e.g. Jaccard entity overlap or inter-
arrival CV), this module builds a **localized statistical baseline** for
every user and scores new sessions against that baseline.

Three sub-signals, combined into a single behavioral anomaly score:

    1. action_distribution — KL-divergence between this session's action-
       type mix and the user's historical distribution.  A user who
       normally browses (view/search) but suddenly fires many trades in
       one session looks anomalous here.

    2. velocity_anomaly — z-score of the current session's actions-per-
       hour versus the user's mean and std-dev.  A sudden spike in
       activity rate is flagged even if the action types look normal.

    3. entity_novelty — fraction of entities in this session that the
       user has *never* interacted with before.  A high novelty rate
       (many unseen symbols) suggests account take-over or scraping.

Each sub-signal is normalized to [0, 1] where 1.0 = completely normal.
The three signals are blended with tunable weights and returned as a
single float score that slots directly into trust_score.py.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Tunable parameters
# ---------------------------------------------------------------------------

# Minimum history (events) required before the model scores; below this
# we return a lenient neutral score so new users aren't penalised.
MIN_HISTORY_EVENTS = 10

# Weights for the three sub-signals (must sum to 1.0)
SIGNAL_WEIGHTS: Dict[str, float] = {
    "action_distribution": 0.40,
    "velocity":            0.35,
    "entity_novelty":      0.25,
}

# Rolling window used to define the user's "recent" baseline (days)
BASELINE_WINDOW_DAYS = 30

# How many standard deviations above the mean before we cap velocity
VELOCITY_ZSCORE_CAP = 3.0

# Action types known to the system
KNOWN_ACTIONS = ("view", "search", "watchlist_add", "alert_set", "trade")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kl_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """
    Smoothed KL divergence KL(P || Q).

    Laplace-smoothed so zero-probability actions don't blow up.
    Returns a non-negative float; 0.0 means identical distributions.
    """
    alpha = 1e-6  # Laplace smoothing constant
    all_keys = set(p) | set(q) | set(KNOWN_ACTIONS)
    total_p = sum(p.values()) + alpha * len(all_keys)
    total_q = sum(q.values()) + alpha * len(all_keys)

    kl = 0.0
    for k in all_keys:
        p_k = (p.get(k, 0.0) + alpha) / total_p
        q_k = (q.get(k, 0.0) + alpha) / total_q
        kl += p_k * math.log(p_k / q_k)
    return kl


def _kl_to_score(kl: float) -> float:
    """
    Map KL divergence → trust score in [0, 1].

    kl == 0   → 1.0  (distributions identical)
    kl == 1   → ~0.37
    kl → ∞   → 0.0
    """
    return math.exp(-kl)


def _zscore_to_score(z: float) -> float:
    """
    Map |z-score| → trust score in [0, 1].

    |z| == 0  → 1.0  (exactly on the mean)
    |z| == 3  → ~0.22 (very far from mean)
    """
    z = min(abs(z), VELOCITY_ZSCORE_CAP)
    return math.exp(-(z ** 2) / 2.0)


# ---------------------------------------------------------------------------
# Core scorer
# ---------------------------------------------------------------------------

class BehavioralAnomalyScorer:
    """
    Localized per-user behavioral anomaly scorer.

    Usage::

        scorer = BehavioralAnomalyScorer(db, user_id)
        score  = await scorer.score(session_events)

    ``session_events`` is a list of dicts with at minimum:
        {
            "action_type": str,     # "view" | "search" | "trade" | …
            "symbol":      str,     # asset identifier
            "occurred_at": datetime
        }
    """

    def __init__(self, db: AsyncSession, user_id: int) -> None:
        self.db = db
        self.user_id = user_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def score(
        self,
        session_events: Optional[List[Dict]] = None,
        window_hours: float = 1.0,
    ) -> float:
        """
        Compute behavioral anomaly score for *this* user.

        Args:
            session_events:
                Events from the *current* session (not yet persisted).
                Each item must have ``action_type``, ``symbol``, and
                ``occurred_at`` keys.  Pass ``None`` or ``[]`` when no
                live session data is available — the scorer will pull
                the user's most-recent events from the DB and score
                those instead.
            window_hours:
                Duration (in hours) that defines a "session" for
                velocity calculation.

        Returns:
            float in [0.0, 1.0]
            1.0  — behaviour is entirely consistent with the baseline
            0.0  — behaviour is maximally anomalous
        """
        history = await self._fetch_history()

        # Not enough data to build a reliable baseline — be lenient
        if len(history) < MIN_HISTORY_EVENTS:
            return 0.75

        # Resolve the session we are scoring
        if not session_events:
            session_events = await self._fetch_recent_session(window_hours)

        # If there's still nothing to score (completely inactive), neutral
        if not session_events:
            return 0.75

        # --- Sub-signal 1: action type distribution ---
        dist_score = self._score_action_distribution(history, session_events)

        # --- Sub-signal 2: velocity ---
        vel_score = self._score_velocity(history, session_events, window_hours)

        # --- Sub-signal 3: entity novelty ---
        nov_score = self._score_entity_novelty(history, session_events)

        # Weighted combination
        composite = (
            dist_score * SIGNAL_WEIGHTS["action_distribution"]
            + vel_score * SIGNAL_WEIGHTS["velocity"]
            + nov_score * SIGNAL_WEIGHTS["entity_novelty"]
        )
        return float(np.clip(composite, 0.0, 1.0))

    # ------------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------------

    async def _fetch_history(self) -> List[Dict]:
        """
        Fetch the user's activity events from the last BASELINE_WINDOW_DAYS.
        """
        from shadowwatch.models.activity import UserActivityEvent

        cutoff = datetime.now(timezone.utc) - timedelta(days=BASELINE_WINDOW_DAYS)
        result = await self.db.execute(
            select(UserActivityEvent)
            .where(
                UserActivityEvent.user_id == self.user_id,
                UserActivityEvent.occurred_at >= cutoff,
            )
            .order_by(UserActivityEvent.occurred_at.asc())
        )
        rows = result.scalars().all()
        return [
            {
                "action_type": r.action_type,
                "symbol": r.symbol,
                "occurred_at": r.occurred_at,
            }
            for r in rows
        ]

    async def _fetch_recent_session(self, window_hours: float) -> List[Dict]:
        """
        Fetch events from the most recent session window from the DB.
        """
        from shadowwatch.models.activity import UserActivityEvent

        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        result = await self.db.execute(
            select(UserActivityEvent)
            .where(
                UserActivityEvent.user_id == self.user_id,
                UserActivityEvent.occurred_at >= cutoff,
            )
            .order_by(UserActivityEvent.occurred_at.asc())
        )
        rows = result.scalars().all()
        return [
            {
                "action_type": r.action_type,
                "symbol": r.symbol,
                "occurred_at": r.occurred_at,
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Sub-signal scorers
    # ------------------------------------------------------------------

    @staticmethod
    def _score_action_distribution(
        history: List[Dict],
        session: List[Dict],
    ) -> float:
        """
        Compare session action-type distribution against historical baseline.

        Uses smoothed KL divergence so the score degrades smoothly as
        the session's action mix drifts from the user's norm.
        """
        historical_counts = Counter(e["action_type"] for e in history)
        session_counts = Counter(e["action_type"] for e in session)

        total_hist = sum(historical_counts.values()) or 1
        total_sess = sum(session_counts.values()) or 1

        hist_dist = {k: v / total_hist for k, v in historical_counts.items()}
        sess_dist = {k: v / total_sess for k, v in session_counts.items()}

        kl = _kl_divergence(sess_dist, hist_dist)
        return _kl_to_score(kl)

    @staticmethod
    def _score_velocity(
        history: List[Dict],
        session: List[Dict],
        window_hours: float,
    ) -> float:
        """
        Compare current session velocity (actions/hour) against baseline.

        Baseline = rolling hourly event counts from history.
        Score degrades if current velocity is a statistical outlier.
        """
        if not history or window_hours <= 0:
            return 1.0

        # Build hourly buckets from history
        oldest = history[0]["occurred_at"]
        newest = history[-1]["occurred_at"]
        total_hours = max(
            (newest - oldest).total_seconds() / 3600.0,
            1.0,  # at least 1 hour window
        )
        # Sliding window counts: split history into 1-hour slots
        hourly_counts: List[float] = []
        slot_start = oldest
        while slot_start < newest:
            slot_end = slot_start + timedelta(hours=1)
            count = sum(
                1
                for e in history
                if slot_start <= e["occurred_at"] < slot_end
            )
            hourly_counts.append(float(count))
            slot_start = slot_end

        if not hourly_counts:
            return 1.0

        mean_vel = float(np.mean(hourly_counts))
        std_vel = float(np.std(hourly_counts)) if len(hourly_counts) > 1 else 0.0

        # Current session velocity
        current_vel = len(session) / window_hours

        if std_vel < 1e-6:
            # No variance in history — only flag huge spikes
            z = (current_vel - mean_vel) / max(mean_vel, 1.0)
        else:
            z = (current_vel - mean_vel) / std_vel

        return _zscore_to_score(z)

    @staticmethod
    def _score_entity_novelty(
        history: List[Dict],
        session: List[Dict],
    ) -> float:
        """
        Penalise sessions that hit many entities the user has never seen.

        A genuine user might occasionally explore new symbols, but a high
        fraction of unseen entities is a strong ATO / scraping indicator.
        """
        known_entities: Set[str] = {e["symbol"] for e in history}
        if not known_entities:
            return 0.75  # No baseline — lenient

        session_symbols = [e["symbol"] for e in session]
        if not session_symbols:
            return 1.0

        novel = sum(1 for s in session_symbols if s not in known_entities)
        novelty_rate = novel / len(session_symbols)

        # Score = 1 − novelty_rate, softened slightly
        # 0% novel  → 1.0   (all familiar)
        # 50% novel → 0.5
        # 100% novel → 0.0  (completely unknown territory)
        return float(1.0 - novelty_rate)


# ---------------------------------------------------------------------------
# Convenience async function (used by trust_score.py)
# ---------------------------------------------------------------------------

async def score_behavioral_anomaly(
    db: AsyncSession,
    user_id: int,
    session_events: Optional[List[Dict]] = None,
    window_hours: float = 1.0,
) -> float:
    """
    Top-level helper that instantiates :class:`BehavioralAnomalyScorer`
    and returns the composite anomaly score.

    Args:
        db:             Async SQLAlchemy session.
        user_id:        User to score.
        session_events: Optional live session events (list of dicts with
                        ``action_type``, ``symbol``, ``occurred_at``).
        window_hours:   Session window for velocity calculation.

    Returns:
        float in [0.0, 1.0] — higher is more normal.
    """
    scorer = BehavioralAnomalyScorer(db, user_id)
    return await scorer.score(session_events, window_hours)
