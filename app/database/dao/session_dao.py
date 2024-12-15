from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.tables.models import GameSession


class SessionDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_session(self, username: str, platform: str) -> GameSession:
        game_session = GameSession(user_id=username, platform=platform)
        self.db_session.add(game_session)
        await self.db_session.commit()
        await self.db_session.refresh(game_session)
        return game_session

    async def end_session(self, session_id: int) -> GameSession:
        result = await self.db_session.execute(select(GameSession).filter(GameSession.id == session_id))
        game_session = result.scalar()
        if not game_session:
            raise HTTPException(status_code=404, detail="Session not found")

        game_session.session_end = datetime.now()
        await self.db_session.commit()
        return game_session

    async def get_session(self, session_id: int) -> Optional[GameSession]:
        result = await self.db_session.execute(select(GameSession).filter(GameSession.id == session_id))
        return result.scalar()

    async def update_heartbeat(self, session_id: int) -> GameSession:
        result = await self.db_session.execute(select(GameSession).filter(GameSession.id == session_id))
        game_session = result.scalar()
        if not game_session:
            raise HTTPException(status_code=404, detail="Session not found")

        game_session.last_heartbeat = datetime.now()
        await self.db_session.commit()
        await self.db_session.refresh(game_session)
        return game_session

    async def end_expired_sessions(self, expired_time) -> List[GameSession]:
        result = await self.db_session.execute(
            select(GameSession).filter(
                GameSession.session_end == None,  # noqa: E711
                GameSession.last_heartbeat < expired_time,
            )
        )
        sessions = result.scalars().all()
        for session in sessions:
            session.session_end = datetime.now()

        await self.db_session.commit()
        return sessions
