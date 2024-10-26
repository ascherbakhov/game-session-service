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