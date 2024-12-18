import asyncio
from datetime import datetime, timedelta
from typing import Optional

from app.api.v1.DTOs.game_session import SessionDTO, HeartbeatDTO
from app.core.logging import session_logger
from app.database.dao.redis.game_session_cache_dao import GameSessionCacheDAO
from app.database.dao.game_session_dao import GameSessionDAO
from app.database.tables.models import User


class SessionsService:
    def __init__(
        self,
        sessions_cache_dao: GameSessionCacheDAO,
        session_dao: GameSessionDAO,
        expired_session_timeout: int,
        request_id: str = None,
    ):
        self.__session_cache_dao = sessions_cache_dao
        self.__session_dao = session_dao
        self.__request_id = request_id or "no-request-context"
        self.__expired_session_timeout = expired_session_timeout

    async def start_session(self, current_user: User, platform: str) -> SessionDTO:
        session_logger.info(
            f"[RequestID={self.__request_id}] Start session for user {current_user.id} on platform {platform}"
        )

        session = await self.__session_dao.get_session_for_user(current_user.username)
        if session:
            await self.end_session(current_user, session.id)

        session = await self.__session_dao.create_session(current_user.username, platform)

        session_dto = SessionDTO(
            session_id=session.id,
            user_id=current_user.username,
            session_start=session.session_start.isoformat(),
            session_end=session.session_end.isoformat() if session.session_end else None,
        )

        await self.__session_cache_dao.save_session_to_cache(session.id, session_dto)
        await self.__session_cache_dao.set_current_session_for_user(current_user.username, session.id)

        return session_dto

    async def end_session(self, current_user: User, session_id: int) -> SessionDTO:
        session_logger.info(f"[RequestID={self.__request_id}] End session {session_id} for user {current_user.id}")

        session = await self.__session_dao.end_session(session_id)

        await self.__session_cache_dao.invalidate_user_session_if_exists(current_user.username)
        await self.__session_cache_dao.delete_session_from_cache(session_id)

        session_dto = SessionDTO(
            session_id=session.id,
            user_id=session.user_id,
            session_start=session.session_start.isoformat(),
            session_end=session.session_end.isoformat(),
        )
        return session_dto

    async def heartbit(self, session_id: int) -> HeartbeatDTO:
        session = await self.__session_dao.update_heartbeat(session_id)
        heartbit_dto = HeartbeatDTO(
            session_id=session.id, user_id=session.user_id, last_heartbeat=session.last_heartbeat.isoformat()
        )
        return heartbit_dto

    async def get_session(self, session_id: int) -> Optional[dict]:
        session_data = await self.__session_cache_dao.get_session_from_cache(session_id)
        if session_data:
            return session_data

        session = await self.__session_dao.get_session(session_id)
        if not session:
            return None

        session_dto = SessionDTO(
            session_id=session.id,
            user_id=session.user_id,
            session_start=session.session_start.isoformat(),
            session_end=session.session_end.isoformat() if session.session_end else None,
        )

        await self.__session_cache_dao.save_session_to_cache(session_id, session_dto)
        return session_data

    async def end_expired_sessions(self) -> None:
        expired_time = datetime.now() - timedelta(minutes=self.__expired_session_timeout)
        expired_sessions = await self.__session_dao.end_expired_sessions(expired_time)

        tasks = []
        for session in expired_sessions:
            tasks.append(self.__session_cache_dao.invalidate_user_session_if_exists(session.user_id))
            tasks.append(self.__session_cache_dao.delete_session_from_cache(session.id))

        await asyncio.gather(*tasks)
