from fastapi_limiter import FastAPILimiter
from starlette.requests import Request

from app.api.v1.dependencies import get_auth_service
from app.core import database
from app.core.redis import get_cache


async def user_identifier(request: Request):
    async with database.async_session_maker() as db:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return "anonymous"
        auth_service = get_auth_service(db)

        user = await auth_service.get_user_by_token(token)
        if not user:
            return "anonymous"

        return f"user:{user.username}"


async def init_rate_limiter():
    cache = get_cache()
    await FastAPILimiter.init(cache)
    FastAPILimiter.identifier = user_identifier


async def close_rate_limiter():
    await FastAPILimiter.close()
