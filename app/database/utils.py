import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = None
async_session_maker = None


def init_engine():
    global engine, async_session_maker
    if engine is None:
        DATABASE_URL = os.getenv("DATABASE_URL")
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session_maker = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_maker is None:
        init_engine()
    async with async_session_maker() as db:
        yield db
