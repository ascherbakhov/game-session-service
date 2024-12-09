import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import app_config
from app.handlers.main_app import app
from tests.factories import UserFactory, TEST_PASSWORD


@pytest.fixture
def async_engine():
    return create_async_engine(app_config.database_url, echo=True)

@pytest.fixture
def async_session_maker(async_engine):
    return async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture
def async_client():
    client = AsyncClient(app=app, base_url="http://test")
    return client

@pytest.fixture
async def test_user(async_session_maker):
    async with async_session_maker() as async_session:
        user = await UserFactory.create(session=async_session)
        return user


@pytest.fixture
async def auth_headers(test_user, async_client):
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post(
            "/api/v1/token",
            data={"username": test_user.username, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        user_token = response.json()["access_token"]
        return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def internal_token_headers():
    return {"X-Internal-Token": app_config.internal_token}
