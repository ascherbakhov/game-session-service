import json


from app.config import app_config


import redis.asyncio as redis
from typing import Optional

redis_client = redis.from_url(app_config.redis_url, decode_responses=True)


USER_SESSION_KEY = "user_session:{}"  # Ключ для хранения текущей сессии юзера
SESSION_KEY = "session:{}"  # Ключ для хранения данных сессии


async def get_session_from_cache(session_id: int) -> Optional[dict]:
    session_data = await redis_client.get(SESSION_KEY.format(session_id))
    if session_data:
        return json.loads(session_data)
    return None


async def save_session_to_cache(session_id: int, session_data: dict, ttl: int = 3600):
    await redis_client.set(SESSION_KEY.format(session_id), json.dumps(session_data), ex=ttl)


async def delete_session_from_cache(session_id: int):
    await redis_client.delete(SESSION_KEY.format(session_id))


async def get_current_session_id_for_user(user_id: str) -> Optional[int]:
    session_id = await redis_client.get(USER_SESSION_KEY.format(user_id))
    if session_id:
        return int(session_id)
    return None


async def set_current_session_for_user(user_id: str, session_id: int, ttl: int = 3600):
    await redis_client.set(USER_SESSION_KEY.format(user_id), str(session_id), ex=ttl)


async def invalidate_user_session_if_exists(user_id: str):
    current_session_id = await get_current_session_id_for_user(user_id)
    if current_session_id:
        await delete_session_from_cache(current_session_id)
        await redis_client.delete(USER_SESSION_KEY.format(user_id))
