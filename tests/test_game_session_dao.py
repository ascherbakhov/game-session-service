from datetime import datetime, timedelta

import pytest

from app.database.dao.GameSessionDAO import GameSessionDAO
from app.database.tables.models import GameSession
from app.database.utils import get_db
from .factories import GameSessionFactory

import pytest


@pytest.mark.asyncio
async def test_get_created_session(user_token, async_client):
    headers = {"Authorization": f"Bearer {user_token}"}

    async with async_client:
        response = await async_client.post(
            "/api/v1/sessions/start/",
            json={"user_id": "test_user", "platform": "Linux"},
            headers=headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        session_id = response_data["session_id"]

        response = await async_client.get(f"/api/v1/sessions/{session_id}", headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["user_id"] == "test_user"
    assert "session_start" in response_data



@pytest.mark.asyncio
async def test_end_session():
    async_session = await anext(get_db())
    dao = GameSessionDAO(async_session)

    session = await GameSessionFactory.create(session=async_session)

    ended_session = await dao.end_session(session.id)

    assert ended_session.session_end is not None
    assert ended_session.id == session.id


@pytest.mark.asyncio
async def test_get_session():
    async_session = await anext(get_db())
    dao = GameSessionDAO(async_session)

    session = await GameSessionFactory.create(session=async_session)

    fetched_session = await dao.get_session(session.id)

    assert fetched_session is not None
    assert fetched_session.id == session.id


@pytest.mark.asyncio
async def test_update_heartbeat():
    async_session = await anext(get_db())
    dao = GameSessionDAO(async_session)

    session = await GameSessionFactory.create(session=async_session)

    updated_session = await dao.update_heartbeat(session.id)

    assert updated_session.last_heartbeat > session.last_heartbeat


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
