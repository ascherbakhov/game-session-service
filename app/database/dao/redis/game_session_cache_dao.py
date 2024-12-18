import json
from typing import Optional

from redis import RedisError

from app.api.v1.DTOs.game_session import SessionDTO
from app.core.logging import session_logger


class GameSessionCacheDAO:
    USER_SESSION_KEY = "user_session:{}"
    SESSION_KEY = "session:{}"

    def __init__(self, redis_cache):
        self.redis_cache = redis_cache

    async def get_session_from_cache(self, session_id: int) -> Optional[dict]:
        try:
            session_data = await self.redis_cache.get(self.SESSION_KEY.format(session_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting sessions from cache")
            return None

        if session_data:
            return json.loads(session_data)
        return None

    async def save_session_to_cache(self, session_id: int, session_data: SessionDTO, ttl: int = 3600):
        try:
            await self.redis_cache.set(self.SESSION_KEY.format(session_id), json.dumps(dict(session_data)), ex=ttl)
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting sessions from cache")

    async def delete_session_from_cache(self, session_id: int):
        try:
            await self.redis_cache.delete(self.SESSION_KEY.format(session_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while deleting sessions from cache")
            return None

    async def get_current_session_id_for_user(self, user_id: str) -> Optional[int]:
        try:
            session_id = await self.redis_cache.get(self.USER_SESSION_KEY.format(user_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting current session")
            return None

        if session_id:
            return int(session_id)
        return None

    async def set_current_session_for_user(self, user_id: str, session_id: int, ttl: int = 3600):
        try:
            await self.redis_cache.set(self.USER_SESSION_KEY.format(user_id), str(session_id), ex=ttl)
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while setting session")
            return None

    async def invalidate_user_session_if_exists(self, user_id: str):
        try:
            current_session_id = await self.get_current_session_id_for_user(user_id)

            if current_session_id:
                await self.delete_session_from_cache(current_session_id)
                await self.redis_cache.delete(self.USER_SESSION_KEY.format(user_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while invalidating session")
            return None
