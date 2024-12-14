from fastapi_limiter import FastAPILimiter
from starlette.requests import Request

from app.api.v1.dependencies import get_auth_service
from app.core.database import get_db
from app.core.redis import redis_client


async def user_identifier(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return "anonymous"
    db = await anext(get_db())
    auth_service = get_auth_service(db)

    user = await auth_service.get_user_by_token(token)
    if not user:
        return "anonymous"

    return f"user:{user.username}"


async def init_rate_limiter():
    await FastAPILimiter.init(redis_client)
    FastAPILimiter.identifier = user_identifier


async def close_rate_limiter():
    await FastAPILimiter.close()
