import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from shadowwatch.invariant import calculate_distance, InvariantState
from shadowwatch.main import ShadowWatch

@pytest.mark.asyncio
async def test_forensic_deltas():
    """Verify that calculate_distance returns per-feature deltas"""
    x_t = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    mu = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    sigma_squared = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    
    distance, deltas = calculate_distance(x_t, mu, sigma_squared)
    
    assert distance > 0
    assert "session_duration" in deltas
    assert deltas["session_duration"] == pytest.approx(1.0)
    assert deltas["inter_session_gap"] == 0.0

@pytest.mark.asyncio
async def test_resolve_divergence():
    """Verify that resolve_divergence correctly updates the event and baseline"""
    sw = ShadowWatch(database_url="postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test")
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = ["user_123"]
    mock_db.execute.return_value = mock_result
    
    with patch.object(sw, 'AsyncSessionLocal', return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_db), __aexit__=AsyncMock())):
        res = await sw.resolve_divergence(1, "legitimate_change", "User reset")
        
        assert res["success"] is True
        assert res["user_id"] == "user_123"
        
        # Verify 3 execute calls: 1. Update event, 2. Update baseline, 3. Commit (implicit in context manager? No, explicit in code)
        # Actually our code has 2 executes + 1 commit.
        assert mock_db.execute.call_count == 2
        mock_db.commit.assert_called_once()
        
        # Check second call (baseline reset)
        args, _ = mock_db.execute.call_args_list[1]
        assert "UPDATE invariant_state" in str(args[0])
        assert args[1]["u"] == "user_123"
