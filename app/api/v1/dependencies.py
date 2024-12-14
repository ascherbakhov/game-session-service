from fastapi import HTTPException
from fastapi.params import Depends
from starlette import status
from starlette.requests import Request

from app.api.v1.handlers.external.utils import oauth2_scheme
from app.api.v1.services.sessions_service import SessionsService
from app.api.v1.services.auth_service import AuthService
from app.core.config import app_config
from app.core.database import get_db
from app.core.redis import get_cache
from app.database.dao.redis.session_cache_dao import SessionCacheDAO
from app.database.dao.session_dao import GameSessionDAO
from app.database.dao.users_dao import UsersDAO


def get_session_service(db=Depends(get_db), cache=Depends(get_cache)):
    session_cache_dao = SessionCacheDAO(cache)
    session_dao = GameSessionDAO(db)
    return SessionsService(session_cache_dao, session_dao)


async def verify_internal_access(request: Request):
    internal_token = request.headers.get("X-Internal-Token")
    if internal_token != app_config.internal_token:
        raise HTTPException(status_code=403, detail="Forbidden")


def get_auth_service(db=Depends(get_db)):
    users_dao = UsersDAO(db)
    return AuthService(users_dao)


async def get_current_user(auth_service: AuthService = Depends(get_auth_service), token=Depends(oauth2_scheme)):
    current_user = await auth_service.get_user_by_token(token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
