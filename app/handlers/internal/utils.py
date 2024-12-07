import json


from app.config import app_config


import redis.asyncio as redis
from typing import Optional

redis_client = redis.from_url(app_config.redis_url, decode_responses=True)


async def get_session_from_cache(session_id: int) -> Optional[dict]:
    session_data = await redis_client.get(f"session:{session_id}")
    if session_data:
        return json.loads(session_data)
    return None


async def save_session_to_cache(session_id: int, session_data: dict, ttl: int = 3600):
    await redis_client.set(f"session:{session_id}", json.dumps(session_data), ex=ttl)


async def delete_session_from_cache(session_id: int):
    await redis_client.delete(f"session:{session_id}")
