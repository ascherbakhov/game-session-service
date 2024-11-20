import asyncio
import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database.tables.models import Base
from app.database.utils import get_db
from app.handlers.game_session_logger import app


@pytest.fixture(scope='session')
def asyncEngine():
    return create_async_engine(os.environ['DATABASE_URL'], echo=True)


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
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"


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
