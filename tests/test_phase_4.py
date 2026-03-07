import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from shadowwatch.main import ShadowWatch
from shadowwatch.invariant.integration import calculate_continuity_impl

@pytest.mark.asyncio
async def test_webhook_alerting():
    """Verify that a webhook is fired on behavioral divergence"""
    sw = ShadowWatch(
        database_url="postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test",
        webhook_url="https://mock-siem.local/events"
    )
    
    mock_db = AsyncMock()
    # Mock return state for calculate_continuity_impl
    # (Simplified: we won't run the full impl, we'll test the ShadowWatch._fire_webhook method directly 
    # and then integration in calculate_continuity_impl if possible)
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        test_event = {"user_id": "user_1", "mode": "shock"}
        await sw._fire_webhook(test_event)
        
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://mock-siem.local/events"
        assert kwargs["json"] == test_event

@pytest.mark.asyncio
async def test_system_stats():
    """Verify global system stats retrieval"""
    sw = ShadowWatch(database_url="postgresql+asyncpg://postgres:password@localhost:5432/shadowwatch_test")
    
    mock_db = AsyncMock()
    mock_res_users = MagicMock()
    mock_res_users.scalar.return_value = 10
    
    mock_res_events = MagicMock()
    mock_res_events.scalar.return_value = 2
    
    mock_res_last = MagicMock()
    mock_res_last.scalar.return_value = None
    
    # Sequential mock execution results
    mock_db.execute.side_effect = [mock_res_users, mock_res_events, mock_res_last]
    
    with patch.object(sw, 'AsyncSessionLocal', return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_db), __aexit__=AsyncMock())):
        stats = await sw.get_system_stats()
        
        assert stats["total_monitored_users"] == 10
        assert stats["unresolved_alerts"] == 2
        assert mock_db.execute.call_count == 3
