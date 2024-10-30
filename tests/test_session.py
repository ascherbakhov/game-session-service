import time
from datetime import datetime, timezone, timedelta

import pytest
from freezegun import freeze_time
from httpx import AsyncClient

from app.database.GameSessionDAO import GameSessionDAO, AsyncSessionLocal
from app.handlers.game_session_logger import app


@pytest.mark.asyncio
async def test_start_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/sessions/start/", json={"user_id": "test_user", "platform": "Linux"})

    assert response.status_code == 200

    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["user_id"] == "test_user"
    assert "session_start" in response_data

@pytest.mark.asyncio
async def test_get_created_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/sessions/start/", json={"user_id": "test_user", "platform": "Linux"})
        assert response.status_code == 200
        response_data = response.json()
        response = await ac.get(f"/sessions/{response_data['session_id']}")

    assert response.status_code == 200

    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["user_id"] == "test_user"
    assert ("session_start" in response_data)

@pytest.mark.asyncio
async def test_heartbit_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/sessions/start/", json={"user_id": "test_user", "platform": "Linux"})
        assert response.status_code == 200
        response_data = response.json()
        current_time = time.time()
        response = await ac.post(f"/sessions/heartbeat/{response_data['session_id']}")

    assert response.status_code == 200

    response_data = response.json()
    assert "last_heartbeat" in response_data

    last_heartbeat = (
        datetime.
        strptime(response_data["last_heartbeat"], "%Y-%m-%dT%H:%M:%S.%f").
        replace(tzinfo=timezone.utc).
        timestamp()
    )

    assert last_heartbeat > current_time


@pytest.mark.asyncio
async def test_end_expired_sessions():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/sessions/start/", json={"user_id": "test_user", "platform": "Linux"})
        assert response.status_code == 200
        session_id = response.json()['session_id']

    with freeze_time(datetime.utcnow() + timedelta(minutes=8)):
        async with AsyncSessionLocal() as session:
            dao = GameSessionDAO(session)
            await dao.end_expired_sessions()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/sessions/{session_id}")
        response_data = response.json()
        assert response_data['session_end']
