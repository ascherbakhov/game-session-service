import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import app_config
from app.database.dao.GameSessionDAO import GameSessionDAO
from app.database.dao.UsersDAO import UsersDAO
from app.database.tables.models import Base
from app.database.utils import get_db
from app.handlers.main_app import app
from tests.factories import UserFactory


@pytest.fixture(scope='session')
def asyncEngine():
    return create_async_engine(app_config.database_url, echo=True)


@pytest.fixture(scope='session')
def asyncSessionLocal(asyncEngine):
    return sessionmaker(bind=asyncEngine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def create_db(asyncEngine):
    async with asyncEngine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Test database created.")


async def drop_db(asyncEngine):
    async with asyncEngine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Test database dropped.")


@pytest.fixture(scope="session", autouse=True)
def set_test_database_url():
    app_config.database_url = "sqlite+aiosqlite:///file::memory:?cache=shared"


@pytest.fixture(scope="function", autouse=True)
def setup_test_db(event_loop, asyncEngine, asyncSessionLocal):
    async def _get_test_db():
        async with asyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db(asyncEngine))
    yield
    loop.run_until_complete(drop_db(asyncEngine))
    app.dependency_overrides.clear()


@pytest.fixture
def async_client():
    return AsyncClient(app=app, base_url="http://test")

@pytest.fixture
async def test_user():
    async_session = await anext(get_db())

    user = await UserFactory.create(session=async_session)
    return user


@pytest.fixture
async def user_token(test_user, async_client):
    async with async_client:
        response = await async_client.post(
            "/login",
            data={"username": test_user.username, "password": test_user.password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        return response.json()["access_token"]