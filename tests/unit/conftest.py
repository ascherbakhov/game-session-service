import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import app_config
from app.database.tables.models import Base


@pytest.fixture(scope='function')
def async_engine():
    return create_async_engine(app_config.database_url, echo=True)


@pytest.fixture(scope='function')
def async_session_local(async_engine):
    return sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def create_db(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Test database created.")


async def drop_db(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Test database dropped.")


@pytest.fixture(scope="session", autouse=True)
def set_test_database_url():
    app_config.database_url = "sqlite+aiosqlite:///file::memory:?cache=shared"


@pytest.fixture(scope="function", autouse=True)
def setup_test_db(async_engine, async_session_local):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(create_db(async_engine))
    yield
    loop.run_until_complete(drop_db(async_engine))
    loop.close()
