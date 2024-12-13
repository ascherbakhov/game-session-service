from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = None
async_session_maker = None


def init_engine(database_url):
    global engine, async_session_maker
    assert engine is None
    engine = create_async_engine(database_url)
    async_session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

def fini_engine():
    global engine, async_session_maker
    assert engine is not None
    engine.dispose()
    engine = None
    async_session_maker = None

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as db:
        yield db
