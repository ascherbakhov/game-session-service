import pytest
from httpx import AsyncClient
from app.game_session_logger import app  # Импортируем ваше FastAPI приложение


@pytest.mark.asyncio
async def test_start_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Делаем POST-запрос к эндпоинту /sessions/start/
        response = await ac.post("/sessions/start/", json={"user_id": "test_user"})

    # Проверяем, что статус ответа - 200 OK
    assert response.status_code == 200

    # Проверяем, что ответ содержит ожидаемые данные
    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["user_id"] == "test_user"
    assert "session_start" in response_data