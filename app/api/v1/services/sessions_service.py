import asyncio
from datetime import datetime, timedelta

from app.core.config import app_config
from app.core.logging import session_logger
from app.database.tables.models import GameSession


class SessionsService:
    def __init__(self, sessions_cache_dao, session_dao, request_id: str = None):
        self.__session_cache_dao = sessions_cache_dao
        self.__session_dao = session_dao
        self.__request_id = request_id or 'no-request-context'

    async def start_session(self, current_user, platform):
        session_logger.info(f"[RequestID={self.__request_id}] Start session for user {current_user.id} on platform {platform}")
        await self.__session_cache_dao.invalidate_user_session_if_exists(current_user.id)

        game_session = GameSession(user_id=current_user.username, platform=platform)
        session = await self.__session_dao.create_session(game_session)

        session_data = {
            "session_id": session.id,
            "user_id": current_user.username,
            "session_start": session.session_start.isoformat(),
            "session_end": session.session_end,
        }

        await self.__session_cache_dao.save_session_to_cache(session.id, session_data)
        await self.__session_cache_dao.set_current_session_for_user(current_user.username, session.id)

        return session_data

    async def end_session(self, current_user, session_id):
        session_logger.info(f"[RequestID={self.__request_id}] End session for user {current_user.id}")
        await self.__session_cache_dao.invalidate_user_session_if_exists(current_user.username)
        await self.__session_cache_dao.delete_session_from_cache(session_id)

        session = await self.__session_dao.end_session(session_id)
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "session_start": session.session_start,
            "session_end": session.session_end,
        }

    async def heartbit(self, session_id):
        session = await self.__session_dao.update_heartbeat(session_id)
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "last_heartbeat": session.last_heartbeat,
        }

    async def get_session(self, session_id):
        session_data = await self.__session_cache_dao.get_session_from_cache(session_id)
        if session_data:
            return session_data

        session = await self.__session_dao.get_session(session_id)
        if not session:
            return None

        session_data = {
            "session_id": session.id,
            "user_id": session.user_id,
            "session_start": session.session_start.isoformat(),
            "session_end": session.session_end.isoformat() if session.session_end else None,
        }

        await self.__session_cache_dao.save_session_to_cache(session_id, session_data)
        return session_data

    async def end_expired_sessions(self):
        expired_time = datetime.now() - timedelta(minutes=app_config.expired_sessions_timeout)
        expired_sessions = await self.__session_dao.end_expired_sessions(expired_time)

        tasks = []
        for session in expired_sessions:
            tasks.append(self.__session_cache_dao.invalidate_user_session_if_exists(session.user_id))
            tasks.append(self.__session_cache_dao.delete_session_from_cache(session.id))

        await asyncio.gather(*tasks)
