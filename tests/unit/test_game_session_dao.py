from datetime import datetime, timedelta

from app.database.dao.session_dao import GameSessionDAO
from app.database.tables.models import GameSession
from app.core.database import get_db
from tests.factories import GameSessionFactory

import pytest


@pytest.mark.asyncio
async def test_create_session():
        async_session = await anext(get_db())
        dao = GameSessionDAO(async_session)
        new_session = await GameSessionFactory.create(session=async_session)

        created_session = await dao.create_session(new_session)

        assert created_session.id is not None
        assert created_session.session_start == new_session.session_start
        assert created_session.session_end == new_session.session_end

        await async_session.close()


@pytest.mark.asyncio
async def test_end_session():
    async_session = await anext(get_db())
    dao = GameSessionDAO(async_session)

    session = await GameSessionFactory.create(session=async_session)

    ended_session = await dao.end_session(session.id)

    assert ended_session.session_end is not None
    assert ended_session.id == session.id

    await async_session.close()



@pytest.mark.asyncio
async def test_get_session():
    async_session = await anext(get_db())
    dao = GameSessionDAO(async_session)

    session = await GameSessionFactory.create(session=async_session)

    fetched_session = await dao.get_session(session.id)

    assert fetched_session is not None
    assert fetched_session.id == session.id

    await async_session.close()



@pytest.mark.asyncio
async def test_update_heartbeat():
    async_session = await anext(get_db())
    dao = GameSessionDAO(async_session)

    session = await GameSessionFactory.create(session=async_session)
    last_heartbit = session.last_heartbeat

    updated_session = await dao.update_heartbeat(session.id)

    assert updated_session.last_heartbeat > last_heartbit

    await async_session.close()



@pytest.mark.asyncio
async def test_end_expired_sessions():
    async_session = await anext(get_db())
    dao = GameSessionDAO(async_session)

    active_session = await GameSessionFactory.create(session=async_session)
    expired_session = await GameSessionFactory.create(
        session=async_session, last_heartbeat=datetime.now() - timedelta(hours=2)
    )

    expired_time = datetime.now() - timedelta(hours=1)
    await dao.end_expired_sessions(expired_time)

    expired_session = await async_session.get(GameSession, expired_session.id)
    active_session = await async_session.get(GameSession, active_session.id)

    assert expired_session.session_end is not None
    assert active_session.session_end is None

    await async_session.close()
