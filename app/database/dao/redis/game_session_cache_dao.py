import json
from typing import Optional

from dulwich.porcelain import reset
from redis import RedisError

from app.DTOs.game_session import SessionDTO
from app.core.logging import session_logger


class GameSessionCacheDAO:
    SESSION_KEY = "session:{}"

    def __init__(self, redis_cache, redis_session_ttl):
        self.__redis_cache = redis_cache
        self.__redis_session_ttl = redis_session_ttl

    async def get_session_from_cache(self, session_id: int) -> Optional[SessionDTO]:
        try:
            session_data = await self.__redis_cache.get(self.SESSION_KEY.format(session_id))
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting sessions from cache")
            return None

        if session_data:
            result = json.loads(session_data)
            return SessionDTO.model_validate(result)
        return None

    async def create_or_update_session(self, session_data: SessionDTO):
        session_logger.debug("Cache session create started")
        try:
            await self.__redis_cache.set(
                self.SESSION_KEY.format(session_data.session_id),
                json.dumps(dict(session_data)),
                ex=self.__redis_session_ttl,
            )
        except RedisError as exc:
            session_logger.exception(f"Exception {exc} occurred while getting sessions from cache")

    async def update_session_ttl(self, session_id):
        session_logger.debug("Update session ttl started")
        await self.__redis_cache.expire(self.SESSION_KEY.format(session_id), self.__redis_session_ttl)
