import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from shadowwatch.core.tracking import TrackingEngine
from shadowwatch.models import Base, UserActivityEvent, UserInterest


async def _setup_tracker():
    """Create an in-memory tracker that does not enforce a specific domain."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session_local = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return TrackingEngine(async_session_local), async_session_local, engine


@pytest.mark.asyncio
async def test_tracking_accepts_custom_domain_metadata():
    tracker, session_factory, engine = await _setup_tracker()

    try:
        await tracker.track(
            user_id=7,
            entity_id="article-123",
            action="read",
            metadata={"asset_type": "article", "pin_interest": True},
        )

        async with session_factory() as session:
            event = (await session.execute(select(UserActivityEvent))).scalar_one()
            interest = (await session.execute(select(UserInterest))).scalar_one()

        assert event.asset_type == "article"
        assert event.symbol == "article-123"
        assert interest.asset_type == "article"
        assert interest.symbol == "article-123"
        assert interest.is_pinned is True
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_tracking_defaults_to_generic_asset_type():
    tracker, session_factory, engine = await _setup_tracker()

    try:
        await tracker.track(
            user_id=8,
            entity_id="playlist-42",
            action="view",
        )

        async with session_factory() as session:
            event = (await session.execute(select(UserActivityEvent))).scalar_one()
            interest = (await session.execute(select(UserInterest))).scalar_one()

        assert event.asset_type == "generic"
        assert interest.asset_type == "generic"
        assert interest.symbol == "playlist-42"
    finally:
        await engine.dispose()
