import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

__engine = None
__async_session_maker = None


def init_engine(database_url: str):
    global __engine, __async_session_maker
    assert __engine is None
    __engine = create_async_engine(database_url)
    __async_session_maker = async_sessionmaker(
        bind=__engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


def fini_engine():
    global __engine, __async_session_maker
    assert __engine is not None
    asyncio.create_task(__engine.dispose())
    __engine = None
    __async_session_maker = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with __async_session_maker() as db:
        yield db


def get_session_maker():
    return __async_session_maker
