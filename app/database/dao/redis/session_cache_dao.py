import json
from typing import Optional

from app.core.redis import redis_client


class SessionCacheDAO:
    USER_SESSION_KEY = "user_session:{}"
    SESSION_KEY = "session:{}"

    def __init__(self, redis_cache):
        self.redis_cache = redis_cache

    async def get_session_from_cache(self, session_id: int) -> Optional[dict]:
        session_data = await redis_client.get(self.SESSION_KEY.format(session_id))
        if session_data:
            return json.loads(session_data)
        return None

    async def save_session_to_cache(self, session_id: int, session_data: dict, ttl: int = 3600):
        await redis_client.set(self.SESSION_KEY.format(session_id), json.dumps(session_data), ex=ttl)

    async def delete_session_from_cache(self, session_id: int):
        await redis_client.delete(self.SESSION_KEY.format(session_id))

    async def get_current_session_id_for_user(self, user_id: str) -> Optional[int]:
        session_id = await redis_client.get(self.USER_SESSION_KEY.format(user_id))
        if session_id:
            return int(session_id)
        return None

    async def set_current_session_for_user(self, user_id: str, session_id: int, ttl: int = 3600):
        await redis_client.set(self.USER_SESSION_KEY.format(user_id), str(session_id), ex=ttl)

    async def invalidate_user_session_if_exists(self, user_id: str):
        current_session_id = await self.get_current_session_id_for_user(user_id)
        if current_session_id:
            await self.delete_session_from_cache(current_session_id)
            await redis_client.delete(self.USER_SESSION_KEY.format(user_id))
