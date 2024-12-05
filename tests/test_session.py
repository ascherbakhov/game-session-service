import time
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from app.handlers.main_app import app


@pytest.mark.asyncio
async def test_start_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/sessions/start/", json={"user_id": "test_user", "platform": "Linux"})

    assert response.status_code == 200

    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["user_id"] == "test_user"
    assert "session_start" in response_data


@pytest.mark.asyncio
async def test_get_created_session(user_token, async_client):
    headers = {"Authorization": f"Bearer {user_token}"}

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
    assert "session_start" in response_data


@pytest.mark.asyncio
async def test_heartbit_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/sessions/start/", json={"user_id": "test_user", "platform": "Linux"})
        assert response.status_code == 200
        response_data = response.json()
        current_time = time.time()
        response = await ac.post(f"/api/v1/sessions/heartbeat/{response_data['session_id']}")

    assert response.status_code == 200

    response_data = response.json()
    assert "last_heartbeat" in response_data

    last_heartbeat = (
        datetime.strptime(response_data["last_heartbeat"], "%Y-%m-%dT%H:%M:%S.%f")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )

    assert last_heartbeat > current_time


@pytest.mark.asyncio
async def test_end_expired_sessions():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/sessions/start/", json={"user_id": "test_user", "platform": "Linux"})
        assert response.status_code == 200
        session_id = response.json()['session_id']

        expired_time = int(time.time() + 10)
        response = await ac.delete("/api/v1/sessions/end_expired?expired_time={}".format(expired_time))
        assert response.status_code == 200

        response = await ac.get(f"/api/v1/sessions/{session_id}")
        response_data = response.json()
        assert response_data['session_end']
