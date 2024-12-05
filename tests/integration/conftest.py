import pytest
from httpx import AsyncClient

from app.database.utils import get_db
from app.handlers.main_app import app
from tests.factories import UserFactory, TEST_PASSWORD


@pytest.fixture
async def async_client():
    client = AsyncClient(app=app, base_url="http://test")
    yield client
    await client.aclose()


@pytest.fixture
async def test_user():
    async_session = await anext(get_db())

    user = await UserFactory.create(session=async_session)
    return user


@pytest.fixture
async def user_token(test_user, async_client):
    response = await async_client.post(
        "/api/v1/token",
        data={"username": test_user.username, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
