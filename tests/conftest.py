import asyncio

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.tables.models import Base
from app.handlers.game_session_logger import app
from app.database.GameSessionDAO import get_db

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Test database created.")

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Test database dropped.")

@pytest.fixture(scope="function", autouse=True)
def setup_test_db(event_loop):
    async def _get_test_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
    yield
    loop.run_until_complete(drop_db())
    app.dependency_overrides.clear()