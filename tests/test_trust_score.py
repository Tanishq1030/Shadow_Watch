"""
Unit tests for Trust Score calculation and ensemble signals.

Tests run without a real database (uses AsyncMock for DB sessions).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from shadowwatch.core.trust_score import (
    calculate_trust_score,
    _score_ip,
    _score_device,
    _score_time_pattern,
    _score_api_behavior,
    WEIGHTS
)


@pytest.mark.asyncio
class TestTrustScoreSignals:

    async def test_score_ip_known_ip(self):
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(ip_address="1.2.3.4")
        db.execute = AsyncMock(return_value=mock_result)

        score = await _score_ip(db, user_id=1, ip="1.2.3.4", country="US")
        assert score == 1.0

    async def test_score_ip_new_ip_known_country(self):
        db = AsyncMock()
        
        # 1. First call: lookup specific IP (None)
        # 2. Second call: lookup country (US history exists)
        mock_ip_res = MagicMock()
        mock_ip_res.scalar_one_or_none.return_value = None
        
        mock_country_res = MagicMock()
        mock_country_res.scalar_one_or_none.return_value = MagicMock(country="US")
        
        db.execute = AsyncMock(side_effect=[mock_ip_res, mock_country_res])

        score = await _score_ip(db, user_id=1, ip="5.6.7.8", country="US")
        assert score == 0.65

    async def test_score_ip_new_user_benefit_of_doubt(self):
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None # No IP history at all
        db.execute = AsyncMock(return_value=mock_result)

        score = await _score_ip(db, user_id=99, ip="1.1.1.1", country="CA")
        assert score == 0.7

    async def test_score_device_known_device(self):
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(trust_level=0.9)
        db.execute = AsyncMock(return_value=mock_result)

        score = await _score_device(db, user_id=1, device_fingerprint="fp123", user_agent="UA")
        assert score == 0.9

    async def test_score_device_unknown(self):
        db = AsyncMock()
        
        # 1. Lookup specific device (None)
        # 2. Lookup any device for this user (History exists)
        mock_dev_res = MagicMock()
        mock_dev_res.scalar_one_or_none.return_value = None
        
        mock_hist_res = MagicMock()
        mock_hist_res.scalar_one_or_none.return_value = MagicMock()
        
        db.execute = AsyncMock(side_effect=[mock_dev_res, mock_hist_res])

        score = await _score_device(db, user_id=1, device_fingerprint="new_fp", user_agent="UA")
        assert score == 0.45

    async def test_score_time_pattern_neutral(self):
        db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = [] # No history
        db.execute = AsyncMock(return_value=mock_res)
        
        score = await _score_time_pattern(db, user_id=1, dt=datetime(2023, 1, 1, 14, 0))
        assert score == 0.7

    async def test_score_time_pattern_matched(self):
        db = AsyncMock()
        mock_res = MagicMock()
        # Mock heatmap: activity mostly at 14:00
        h14 = MagicMock(hour=14, weight=10.0)
        mock_res.scalars.return_value.all.return_value = [h14] 
        db.execute = AsyncMock(return_value=mock_res)
        
        score = await _score_time_pattern(db, user_id=1, dt=datetime(2023, 1, 1, 14, 0))
        assert score > 0.8

    async def test_score_api_behavior_bot_detection(self):
        db = AsyncMock()
        mock_res = MagicMock()
        # Mock 10 events with perfect 1s intervals
        events = []
        for i in range(10):
            ev = MagicMock()
            ev.occurred_at = datetime(2023, 1, 1, 12, 0, i)
            events.append(ev)
        
        mock_res.scalars.return_value.all.return_value = events
        db.execute = AsyncMock(return_value=mock_res)
        
        score = await _score_api_behavior(db, user_id=1)
        assert score <= 0.3 # Bot penalty


@pytest.mark.asyncio
class TestCalculateTrustScore:

    @patch("shadowwatch.core.trust_score._score_api_behavior")
    @patch("shadowwatch.core.trust_score._score_time_pattern")
    @patch("shadowwatch.core.trust_score.verify_fingerprint")
    @patch("shadowwatch.core.trust_score._score_ip")
    @patch("shadowwatch.core.trust_score._score_device")
    async def test_calculate_trust_score_ensemble(self, mock_device, mock_ip, mock_fp, mock_time, mock_api):
        db = AsyncMock()
        mock_ip.return_value = 1.0     # Trusted IP
        mock_device.return_value = 1.0 # Trusted Device
        mock_fp.return_value = 1.0     # Perfect behavioral match
        mock_time.return_value = 1.0   # On pattern
        mock_api.return_value = 1.0    # High jitter (human)
        
        ctx = {
            "ip": "1.2.3.4",
            "device_fingerprint": "fp1",
            "top_entities": {"AAPL"}
        }
        
        result = await calculate_trust_score(db, user_id=1, request_context=ctx)
        
        assert result["trust_score"] == 1.0
        assert result["risk_level"] == "low"
        assert result["action"] == "allow"
        assert result["factors"]["ip_location"] == 1.0
        assert result["factors"]["time_pattern"] == 1.0

    @patch("shadowwatch.core.trust_score._score_api_behavior")
    @patch("shadowwatch.core.trust_score._score_time_pattern")
    @patch("shadowwatch.core.trust_score.verify_fingerprint")
    @patch("shadowwatch.core.trust_score._score_ip")
    @patch("shadowwatch.core.trust_score._score_device")
    async def test_calculate_trust_score_high_risk(self, mock_device, mock_ip, mock_fp, mock_time, mock_api):
        db = AsyncMock()
        mock_ip.return_value = 0.4     # New IP/Country
        mock_device.return_value = 0.45 # New Device
        mock_fp.return_value = 0.0     # Zero behavioral match
        mock_time.return_value = 0.3   # Off pattern
        mock_api.return_value = 0.3    # Bot jitter
        
        result = await calculate_trust_score(db, user_id=1, request_context={})
        
        assert result["trust_score"] < 0.4
        assert result["risk_level"] == "high"
        assert result["action"] == "block"
