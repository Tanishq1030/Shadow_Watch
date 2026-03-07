"""
Unit tests for behavioral fingerprint Jaccard similarity.

Tests run without a database (uses mock DB session).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from shadowwatch.core.fingerprint import _jaccard_similarity, verify_fingerprint


# =====================================================
# Pure function tests (no DB needed)
# =====================================================

class TestJaccardSimilarity:

    def test_identical_sets(self):
        a = {"AAPL", "GOOGL", "MSFT"}
        b = {"AAPL", "GOOGL", "MSFT"}
        assert _jaccard_similarity(a, b) == 1.0

    def test_completely_disjoint(self):
        a = {"AAPL", "GOOGL"}
        b = {"TSLA", "AMZN"}
        assert _jaccard_similarity(a, b) == 0.0

    def test_partial_overlap(self):
        # A ∩ B = {AAPL, GOOGL} → size 2
        # A ∪ B = {AAPL, GOOGL, MSFT, TSLA} → size 4
        # J = 2/4 = 0.5
        a = {"AAPL", "GOOGL", "MSFT"}
        b = {"AAPL", "GOOGL", "TSLA"}
        result = _jaccard_similarity(a, b)
        assert abs(result - 0.5) < 1e-9

    def test_both_empty(self):
        assert _jaccard_similarity(set(), set()) == 1.0

    def test_one_empty(self):
        assert _jaccard_similarity({"AAPL"}, set()) == 0.0
        assert _jaccard_similarity(set(), {"AAPL"}) == 0.0

    def test_subset(self):
        # A ⊂ B: |A∩B| = 2, |A∪B| = 3 → 2/3
        a = {"AAPL", "GOOGL"}
        b = {"AAPL", "GOOGL", "MSFT"}
        result = _jaccard_similarity(a, b)
        assert abs(result - 2/3) < 1e-9

    def test_single_element_match(self):
        a = {"AAPL"}
        b = {"AAPL"}
        assert _jaccard_similarity(a, b) == 1.0

    def test_single_element_no_match(self):
        a = {"AAPL"}
        b = {"TSLA"}
        assert _jaccard_similarity(a, b) == 0.0

    def test_symmetry(self):
        a = {"AAPL", "GOOGL", "MSFT"}
        b = {"AAPL", "TSLA", "AMZN"}
        assert _jaccard_similarity(a, b) == _jaccard_similarity(b, a)


# =====================================================
# verify_fingerprint async tests (mocked DB)
# =====================================================

@pytest.mark.asyncio
class TestVerifyFingerprint:

    async def _make_db(self, top_symbols):
        """Build a mock AsyncSession that returns the given symbols."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [(s,) for s in top_symbols]
        mock_db.execute = AsyncMock(return_value=mock_result)
        return mock_db

    async def test_perfect_match(self):
        entities = {"AAPL", "GOOGL", "MSFT"}
        db = await self._make_db(entities)
        score = await verify_fingerprint(db, user_id=1, client_top_entities=entities)
        assert score == 1.0

    async def test_no_client_entities(self):
        db = await self._make_db({"AAPL", "GOOGL"})
        score = await verify_fingerprint(db, user_id=1, client_top_entities=None)
        assert score == 0.5

    async def test_empty_client_entities(self):
        db = await self._make_db({"AAPL", "GOOGL"})
        score = await verify_fingerprint(db, user_id=1, client_top_entities=set())
        assert score == 0.5

    async def test_no_server_history(self):
        """New user with no tracked entities: benefit of the doubt."""
        db = await self._make_db(set())
        score = await verify_fingerprint(db, user_id=999, client_top_entities={"AAPL"})
        assert score == 0.7

    async def test_partial_overlap(self):
        server = {"AAPL", "GOOGL", "MSFT"}
        client = {"AAPL", "GOOGL", "TSLA"}
        db = await self._make_db(server)
        score = await verify_fingerprint(db, user_id=1, client_top_entities=client)
        # J = 2/4 = 0.5
        assert abs(score - 0.5) < 1e-9

    async def test_zero_overlap(self):
        server = {"AAPL", "GOOGL"}
        client = {"TSLA", "AMZN"}
        db = await self._make_db(server)
        score = await verify_fingerprint(db, user_id=1, client_top_entities=client)
        assert score == 0.0

    async def test_score_range(self):
        """Score must always be in [0.0, 1.0]."""
        for server_size in [0, 1, 5, 10]:
            server = {f"ENT{i}" for i in range(server_size)}
            client = {f"ENT{i}" for i in range(server_size // 2, server_size + 3)}
            db = await self._make_db(server)
            score = await verify_fingerprint(db, user_id=1, client_top_entities=client)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range"
