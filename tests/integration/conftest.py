import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import app_config
from app.main_app import make_app, app_lifespan
from tests.factories import UserFactory, TEST_PASSWORD
from app.main_app import make_app


@pytest.fixture
def app():
    return make_app()


@pytest.fixture
def zero_expired_timeout():
    app_config.expired_sessions_timeout = 0


@pytest.fixture
async def async_engine():
    return create_async_engine(app_config.database_url)

@pytest.fixture
async def async_session_maker(async_engine):
    return async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture
async def async_client(app):
    async with app_lifespan(app):
        client = AsyncClient(app=app, base_url="http://test")
        yield client
        await client.aclose()

@pytest.fixture
async def test_user(async_session_maker):
    async with async_session_maker() as async_session:
        user = await UserFactory.create(session=async_session)
        return user


@pytest.fixture
async def auth_headers(test_user, async_client):
        response = await async_client.post(
            "/api/v1/users/token",
            data={"username": test_user.username, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        user_token = response.json()["access_token"]
        return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def internal_token_headers():
    return {"X-Internal-Token": app_config.internal_token}
