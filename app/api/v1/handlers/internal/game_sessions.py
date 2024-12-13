from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.dependencies import get_session_service
from app.core.database import get_db
from app.core.redis import get_cache
from app.database.dao.redis.session_cache_dao import SessionCacheDAO
from app.database.dao.session_dao import GameSessionDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dao.redis import session_cache_dao
from app.api.v1.handlers.internal.middleware import verify_internal_access

internal_game_session_router = APIRouter(dependencies=[Depends(verify_internal_access)])


@internal_game_session_router.get("/sessions/{session_id}")
async def get_session_internal(session_id: int, session_service=Depends(get_session_service)):
    return await session_service.get_session(session_id)


@internal_game_session_router.delete("/sessions/end_expired")
async def end_expired(expired_time: int, db: AsyncSession = Depends(get_db)):
    dao = GameSessionDAO(db)
    expired_datetime = datetime.fromtimestamp(expired_time)
    await dao.end_expired_sessions(expired_datetime)
    return {"status": "Expired sessions processed"}
