from fastapi.params import Depends

from app.api.v1.services.sessions_service import SessionsService
from app.core.database import get_db
from app.core.redis import get_cache
from app.database.dao.redis.session_cache_dao import SessionCacheDAO
from app.database.dao.session_dao import GameSessionDAO


def get_session_service(db=Depends(get_db), cache=Depends(get_cache)):
    session_cache_dao = SessionCacheDAO(cache)
    session_dao = GameSessionDAO(db)
    return SessionsService(session_cache_dao, session_dao)
