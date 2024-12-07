import redis
from fastapi_limiter import FastAPILimiter
from starlette.requests import Request

from app.config import app_config
from app.database.utils import get_db
from app.handlers.external.users import get_user_from_token


async def user_identifier(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return "anonymous"
    db = await anext(get_db())

    user = await get_user_from_token(token, db)
    if not user:
        return "anonymous"

    return f"user:{user.username}"


async def init_rate_limiter():
    redis_client = redis.from_url(app_config.redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)
    FastAPILimiter.identifier = user_identifier


async def close_rate_limiter():
    await FastAPILimiter.close()
