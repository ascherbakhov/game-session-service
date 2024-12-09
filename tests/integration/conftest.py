import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import app_config
from app.handlers.main_app import make_app, app_lifespan
from tests.factories import UserFactory, TEST_PASSWORD


@pytest.fixture
def app(event_loop):
    return make_app()

@pytest.fixture
def async_engine():
    return create_async_engine(app_config.database_url)

@pytest.fixture
def async_session_maker(async_engine):
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


@pytest.yield_fixture(scope='module')
def event_loop():
    """
    Create an instance of the default event loop for each test case.
    "https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-264418154"
    Not the best result, because tests are not totally isolated, but it works
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
