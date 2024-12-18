import json
from typing import Optional

from redis import RedisError

from app.api.v1.DTOs.game_session import SessionDTO
from app.core.logging import session_logger


class GameSessionCacheDAO:
    USER_SESSION_KEY = "user_session:{}"
    SESSION_KEY = "session:{}"

    def __init__(self, redis_cache, expired_session_ttl):
        self.__redis_cache = redis_cache
        self.__expired_session_ttl = expired_session_ttl

    async def get_session_from_cache(self, session_id: int) -> Optional[dict]:
        try:
            session_data = await self.__redis_cache.get(self.SESSION_KEY.format(session_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting sessions from cache")
            return None

        if session_data:
            return json.loads(session_data)
        return None

    async def update_session(self, session_data: SessionDTO):
        try:
            await self.__redis_cache.set(
                self.SESSION_KEY.format(session_data.session_id), json.dumps(dict(session_data)),
                ex=self.__expired_session_ttl
            )
            await self.__redis_cache.set(
                self.USER_SESSION_KEY.format(session_data.user_id), str(session_data.session_id),
                ex=self.__expired_session_ttl
            )
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting sessions from cache")

    async def update_session_ttl(self, session_id, user_id):
        await self.__redis_cache.expire(
            self.SESSION_KEY.format(session_id), self.__expired_session_ttl
        )
        await self.__redis_cache.expire(
            self.USER_SESSION_KEY.format(user_id), self.__expired_session_ttl
        )

    async def delete_session_from_cache(self, session_id: int):
        try:
            await self.__redis_cache.delete(self.SESSION_KEY.format(session_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while deleting sessions from cache")
            return None

    async def get_current_session_id_for_user(self, user_id: str) -> Optional[int]:
        try:
            session_id = await self.__redis_cache.get(self.USER_SESSION_KEY.format(user_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting current session")
            return None

        if session_id:
            return int(session_id)
        return None

    async def set_current_session_for_user(self, user_id: str, session_id: int, ttl: int = 3600):
        try:
            await self.__redis_cache.set(self.USER_SESSION_KEY.format(user_id), str(session_id), ex=ttl)
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while setting session")
            return None

    async def invalidate_user_session_if_exists(self, user_id: str):
        try:
            current_session_id = await self.get_current_session_id_for_user(user_id)

            if current_session_id:
                await self.delete_session_from_cache(current_session_id)
                await self.__redis_cache.delete(self.USER_SESSION_KEY.format(user_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while invalidating session")
            return None
