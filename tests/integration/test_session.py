import time
from datetime import datetime, timezone

import pytest

from app.handlers.api.v1.schemas.game_sessions import PlatformEnum


@pytest.mark.asyncio
async def test_start_session(auth_headers, async_client):
    response = await async_client.post(
        "/api/v1/sessions/start/", json={"platform": PlatformEnum.linux},
        headers=auth_headers
    )

    assert response.status_code == 200

    response_data = response.json()
    assert "session_id" in response_data
    assert "session_start" in response_data


@pytest.mark.asyncio
async def test_get_created_session(auth_headers, async_client, internal_token_headers):
    response = await async_client.post(
        "/api/v1/sessions/start/",
        json={"platform": PlatformEnum.linux},
        headers=auth_headers,
    )
    assert response.status_code == 200
    response_data = response.json()
    session_id = response_data["session_id"]

    response = await async_client.get(f"/internal/v1/sessions/{session_id}", headers=internal_token_headers)

    assert response.status_code == 200
    response_data = response.json()
    assert "session_id" in response_data
    assert "session_start" in response_data


@pytest.mark.asyncio
async def test_heartbit_session(auth_headers, async_client):
    response = await async_client.post("/api/v1/sessions/start/", json={"platform": PlatformEnum.linux}, headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    current_time = time.time()
    response = await async_client.post(f"/api/v1/sessions/heartbeat/{response_data['session_id']}", headers=auth_headers)

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
async def test_end_expired_sessions(async_client, auth_headers, internal_token_headers, zero_expired_timeout):
    response = await async_client.post("/api/v1/sessions/start/", json={"platform": PlatformEnum.linux}, headers=auth_headers)
    assert response.status_code == 200
    session_id = response.json()['session_id']

    response = await async_client.post(
        "/internal/v1/sessions/end_expired", headers=internal_token_headers
    )
    assert response.status_code == 200

    response = await async_client.get(f"/internal/v1/sessions/{session_id}", headers=internal_token_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_start_session_when_not_ended(auth_headers, async_client, internal_token_headers):
    response = await async_client.post(
        "/api/v1/sessions/start/",
        json={"platform": PlatformEnum.linux},
        headers=auth_headers,
    )
    session_id = response.json()['session_id']

    response = await async_client.post(
        "/api/v1/sessions/start/",
        json={"platform": PlatformEnum.linux},
        headers=auth_headers,
    )
    assert response.status_code == 200

    response = await async_client.get(f"/internal/v1/sessions/{session_id}", headers=internal_token_headers)
    assert response.status_code == 200
    assert response.json()['session_end'] is not None


@pytest.mark.asyncio
async def test_get_session_for_user(auth_headers, async_client, internal_token_headers, test_user):
    await async_client.post(
        "/api/v1/sessions/start/",
        json={"platform": PlatformEnum.linux},
        headers=auth_headers,
    )
    response = await async_client.post(
        "/api/v1/sessions/start/",
        json={"platform": PlatformEnum.linux},
        headers=auth_headers,
    )
    session_id = response.json()['session_id']

    response = await async_client.get(
        f"/internal/v1/users/{test_user.username}/sessions/current",
        headers=internal_token_headers,
    )
    assert response.status_code == 200
    assert session_id == response.json()['session_id']
