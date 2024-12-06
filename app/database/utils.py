from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import app_config

engine = None
async_session_maker = None


def init_engine():
    global engine, async_session_maker
    if engine is None:
        engine = create_async_engine(app_config.database_url, echo=True)
        async_session_maker = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_maker is None:
        init_engine()
    async with async_session_maker() as db:
        yield db
