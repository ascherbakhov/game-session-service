import os
from os.path import dirname

import pytest
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.core.config import app_config
from app.main_app import make_app, app_lifespan
from tests.factories import UserFactory, TEST_PASSWORD


@pytest.fixture
def root_dir():
    return dirname(dirname(dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    return make_app()

@pytest.fixture(scope="function", autouse=True)
async def test_db_with_migrations(root_dir):
    current_dir = os.getcwd()
    os.chdir(root_dir)  # FIXME

    with PostgresContainer("postgres:15") as postgres:
        postgres.start()

        db_url = postgres.get_connection_url()
        db_url_async = db_url.replace('psycopg2', 'asyncpg')
        app_config.database_url = db_url

        alembic_cfg = Config(file_=os.path.join(root_dir, 'alembic.ini'))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(alembic_cfg, "head")

        app_config.database_url = db_url_async

        os.chdir(current_dir)
        yield db_url_async


@pytest.fixture(scope="function", autouse=True)
def test_redis():
    with RedisContainer("redis:7") as redis_container:
        redis_container.start()
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        app_config.redis_url=f'redis://{host}:{port}/0'

        yield


@pytest.fixture
def zero_expired_timeout():
    app_config.expired_sessions_timeout = 0


@pytest.fixture
async def async_engine(test_db_with_migrations):
    return create_async_engine(test_db_with_migrations)

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
            "/api/v1/auth/token",
            data={"username": test_user.username, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        user_token = response.json()["access_token"]
        return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def internal_token_headers():
    return {"X-Internal-Token": app_config.internal_token}
