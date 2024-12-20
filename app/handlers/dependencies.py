from fastapi import HTTPException
from fastapi.params import Depends
from starlette import status
from starlette.requests import Request

from app.core.password_utils import oauth2_scheme
from app.services.sessions_service import SessionsService
from app.services.auth_service import AuthService
from app.core.config import app_config
from app.core.database import get_db
from app.core.redis import get_cache
from app.database.dao.redis.game_session_cache_dao import GameSessionCacheDAO
from app.database.dao.game_session_dao import GameSessionDAO
from app.database.dao.users_dao import UsersDAO
from app.database.tables.models import User


def get_session_service(request: Request = None, db=Depends(get_db), cache=Depends(get_cache)):
    session_cache_dao = GameSessionCacheDAO(cache, app_config.redis.game_session_ttl)
    session_dao = GameSessionDAO(db)

    request_id = None
    if request:
        request_id = getattr(request.state, "request_id", None)

    return SessionsService(session_cache_dao, session_dao, app_config.expired_sessions_timeout, request_id)


async def verify_internal_access(request: Request):
    internal_token = request.headers.get("X-Internal-Token")
    if internal_token != app_config.internal_token:
        raise HTTPException(status_code=403, detail="Forbidden")


def get_auth_service(db=Depends(get_db)) -> AuthService:
    users_dao = UsersDAO(db)
    return AuthService(users_dao=users_dao, authConfig=app_config.auth)


async def get_current_user(auth_service: AuthService = Depends(get_auth_service), token=Depends(oauth2_scheme)) -> User:
    current_user = await auth_service.get_user_by_token(token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
