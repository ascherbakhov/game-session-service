from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = None
async_session_maker = None


def init_engine(database_url):
    global engine, async_session_maker
    if engine is None:
        engine = create_async_engine(database_url)
        async_session_maker = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as db:
        yield db
