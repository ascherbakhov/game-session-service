from datetime import datetime, timedelta
from typing import Optional, Generator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.database.tables.models import GameSession


engine = create_engine("sqlite:///game_sessions.db")
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine,
    class_=AsyncSession, expire_on_commit=False
)

# DAO for accessing game session data
class GameSessionDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_session(self, user_id: str) -> GameSession:
        game_session = GameSession(user_id=user_id)
        self.db_session.add(game_session)
        await self.db_session.commit()
        await self.db_session.refresh(game_session)
        return game_session

    async def end_session(self, session_id: int) -> GameSession:
        result = await self.db_session.execute(select(GameSession).filter(GameSession.id == session_id))
        game_session = result.scalar().first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Session not found")

        game_session.session_end = datetime.utcnow()
        await self.db_session.commit()
        await self.db_session.refresh(game_session)
        return game_session

    async def get_session(self, session_id: int) -> Optional[GameSession]:
        result = await self.db_session.execute(select(GameSession).filter(GameSession.id == session_id))
        return result.scalars().first()

    async def update_heartbeat(self, session_id: int) -> GameSession:
        result = await self.db_session.execute(select(GameSession).filter(GameSession.id == session_id))
        game_session = result.scalars().first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Session not found")

        game_session.last_heartbeat = datetime.utcnow()
        await self.db_session.commit()
        await self.db_session.refresh(game_session)
        return game_session

    async def end_expired_sessions(self):
        expired_time = datetime.utcnow() - timedelta(minutes=10)  # Assume session expires after 10 minutes of inactivity
        result = await self.db_session.execute(
            select(GameSession).filter(GameSession.session_end == None, GameSession.last_heartbeat < expired_time)
        )
        sessions = result.scalars().all()
        for session in sessions:
            session.session_end = datetime.utcnow()

        await self.db_session.commit()


async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()