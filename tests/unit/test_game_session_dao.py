from datetime import datetime, timedelta

from app.database.dao.game_session_dao import GameSessionDAO
from app.database.tables.models import GameSession
from tests.factories import GameSessionFactory

import pytest


@pytest.mark.asyncio
async def test_create_session(async_session_local):
    async with async_session_local() as async_session:
        dao = GameSessionDAO(async_session)

        created_session = await dao.create_session(username="test_user", platform="Linux")

        assert created_session.id is not None


@pytest.mark.asyncio
async def test_end_session(async_session_local):
    async with async_session_local() as async_session:
        dao = GameSessionDAO(async_session)

        session = await GameSessionFactory.create(session=async_session)

        ended_session = await dao.end_session(session.id)

        assert ended_session.session_end is not None
        assert ended_session.id == session.id


@pytest.mark.asyncio
async def test_get_session(async_session_local):
    async with async_session_local() as async_session:
        dao = GameSessionDAO(async_session)

        session = await GameSessionFactory.create(session=async_session)

        fetched_session = await dao.get_session(session.id)

        assert fetched_session is not None
        assert fetched_session.id == session.id


@pytest.mark.asyncio
async def test_update_heartbeat(async_session_local):
    async with async_session_local() as async_session:
        dao = GameSessionDAO(async_session)

        session = await GameSessionFactory.create(session=async_session)
        last_heartbit = session.last_heartbeat

        updated_session = await dao.update_heartbeat(session.id)

        assert updated_session.last_heartbeat > last_heartbit


@pytest.mark.asyncio
async def test_end_expired_sessions(async_session_local):
    async with async_session_local() as async_session:
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
