import asyncio
from datetime import datetime, timedelta
from typing import Optional

from app.DTOs.game_session import SessionDTO, HeartbeatDTO
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
            session_start=session.session_start_iso,
            session_end=session.session_end_iso,
        )

        _ = asyncio.create_task(self.__session_cache_dao.create_or_update_session(session_dto))

        return session_dto

    async def end_session(self, current_user: User, session_id: int) -> SessionDTO:
        session_logger.info(f"[RequestID={self.__request_id}] End session {session_id} for user {current_user.id}")
        session = await self.__session_dao.end_session(session_id)

        session_dto = SessionDTO(
            session_id=session.id,
            user_id=session.user_id,
            session_start=session.session_start_iso,
            session_end=session.session_end_iso,
        )

        _ = asyncio.create_task(self.__session_cache_dao.create_or_update_session(session_dto))

        return session_dto

    async def heartbit(self, session_id: int) -> HeartbeatDTO:
        session = await self.__session_dao.update_heartbeat(session_id)

        heartbit_dto = HeartbeatDTO(
            session_id=session.id, user_id=session.user_id, last_heartbeat=session.last_heartbit_iso
        )

        _ = asyncio.create_task(self.__session_cache_dao.update_session_ttl(session_id))

        return heartbit_dto

    async def get_session(self, session_id: int) -> Optional[dict]:
        session_data = await self.__session_cache_dao.get_session_from_cache(session_id)
        if session_data:
            return session_data

        session = await self.__session_dao.get_session(session_id)
        if not session:
            return None

        session_dto = SessionDTO.create_by_session(session)

        _ = asyncio.create_task(self.__session_cache_dao.create_or_update_session(session_dto))

        return session_data

    async def get_session_by_user(self, user_id: str):
        session = await self.__session_dao.get_session_for_user(user_id)
        if not session:
            return None

        session_dto = SessionDTO.create_by_session(session)

        _ = asyncio.create_task(self.__session_cache_dao.create_or_update_session(session_dto))

        return session_dto

    async def end_expired_sessions(self) -> None:
        expired_time = datetime.now() - timedelta(minutes=self.__expired_session_timeout)
        await self.__session_dao.end_expired_sessions(expired_time)
