import redis

from app.core.config import app_config

redis_client = redis.asyncio.from_url(app_config.redis_url, encoding="utf-8", decode_responses=True)

def get_cache():
    return redis_client