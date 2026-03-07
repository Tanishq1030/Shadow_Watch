"""
Unit tests for Pre-Auth Intent Analysis.

Tests run without a real database (uses AsyncMock for DB sessions).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from shadowwatch.main import ShadowWatch


@pytest.mark.asyncio
class TestPreAuthIntent:

    async def test_pre_auth_intent_new_session(self):
        # Mock DB and ShadowWatch
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        sw = ShadowWatch(database_url="postgresql+asyncpg://dummy:dummy@localhost/dummy")
        sw.AsyncSessionLocal = MagicMock()
        sw.AsyncSessionLocal.return_value.__aenter__.return_value = mock_db
        sw.AsyncSessionLocal.return_value.__aexit__ = AsyncMock()

        observations = {
            "session_id": "sess_001",
            "ip": "1.2.3.4",
            "device_fingerprint": "dev_fp_001",
            "typing_cadence": {"mean": 150, "std": 20}
        }

        result = await sw.pre_auth_intent(identifier="sess_001", observations=observations)

        assert result["session_id"] == "sess_001"
        assert result["intent_score"] == 1.0
        assert result["risk_level"] == "low"
        
        # Verify DB add was called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_pre_auth_intent_update_session(self):
        # Mock existing session
        existing_session = MagicMock()
        existing_session.signals = {"old": "data"}
        
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_session)
        mock_db.execute = AsyncMock(return_value=mock_result)

        sw = ShadowWatch(database_url="postgresql+asyncpg://dummy:dummy@localhost/dummy")
        sw.AsyncSessionLocal = MagicMock()
        sw.AsyncSessionLocal.return_value.__aenter__.return_value = mock_db
        sw.AsyncSessionLocal.return_value.__aexit__ = AsyncMock()

        observations = {
            "session_id": "sess_001",
            "typing_cadence": {"mean": 160}
        }

        await sw.pre_auth_intent(identifier="sess_001", observations=observations)

        # Verify signals were merged
        assert existing_session.signals["old"] == "data"
        assert existing_session.signals["typing_cadence"] == {"mean": 160}
        mock_db.commit.assert_called_once()
