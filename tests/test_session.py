import time
from datetime import datetime

import pytest
from httpx import AsyncClient
from app.handlers.game_session_logger import app


@pytest.mark.asyncio
async def test_start_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/sessions/start/", json={"user_id": "test_user"})

    assert response.status_code == 200

    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["user_id"] == "test_user"
    assert "session_start" in response_data

@pytest.mark.asyncio
async def test_get_created_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/sessions/start/", json={"user_id": "test_user"})
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
        response = await ac.post("/sessions/start/", json={"user_id": "test_user"})
        assert response.status_code == 200
        response_data = response.json()
        current_time = time.time()
        response = await ac.post(f"/sessions/heartbeat/{response_data['session_id']}")

    assert response.status_code == 200

    response_data = response.json()
    assert "last_heartbeat" in response_data

    # Преобразование строки в объект datetime
    last_heartbeat = datetime.strptime(response_data["last_heartbeat"], "%Y-%m-%dT%H:%M:%S.%f")

    # Получение timestamp (метки времени)
    timestamp = last_heartbeat.timestamp()
    assert timestamp > current_time
