import redis
from fastapi_limiter import FastAPILimiter

from app.config import app_config


async def init_rate_limiter():
    redis_client = redis.from_url("redis://redis_cache:6379/0", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)


async def close_rate_limiter():
    await FastAPILimiter.close()
