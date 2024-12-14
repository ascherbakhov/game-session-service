from fastapi import HTTPException
from fastapi.params import Depends
from starlette.requests import Request

from app.api.v1.services.sessions_service import SessionsService
from app.core.config import app_config
from app.core.database import get_db
from app.core.redis import get_cache
from app.database.dao.redis.session_cache_dao import SessionCacheDAO
from app.database.dao.session_dao import GameSessionDAO


def get_session_service(db=Depends(get_db), cache=Depends(get_cache)):
    session_cache_dao = SessionCacheDAO(cache)
    session_dao = GameSessionDAO(db)
    return SessionsService(session_cache_dao, session_dao)


async def verify_internal_access(request: Request):
    internal_token = request.headers.get("X-Internal-Token")
    if internal_token != app_config.internal_token:
        raise HTTPException(status_code=403, detail="Forbidden")
