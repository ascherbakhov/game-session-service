from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.redis import get_cache
from app.database.dao.redis.session_cache_dao import SessionCacheDAO
from app.database.dao.session_dao import GameSessionDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dao.redis import session_cache_dao
from app.api.v1.handlers.internal.middleware import verify_internal_access

internal_game_session_router = APIRouter(dependencies=[Depends(verify_internal_access)])


@internal_game_session_router.get("/sessions/{session_id}")
async def get_session_internal(session_id: int, db: AsyncSession = Depends(get_db), cache=Depends(get_cache)):
    session_cache = SessionCacheDAO(cache)
    session_data = await session_cache.get_session_from_cache(session_id)
    if session_data:
        return session_data

    dao = GameSessionDAO(db)
    session = await dao.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    session_data = {
        "session_id": session.id,
        "user_id": session.user_id,
        "session_start": session.session_start.isoformat(),
        "session_end": session.session_end.isoformat() if session.session_end else None,
    }

    await session_cache.save_session_to_cache(session_id, session_data)
    return session_data


@internal_game_session_router.delete("/sessions/end_expired")
async def end_expired(expired_time: int, db: AsyncSession = Depends(get_db)):
    dao = GameSessionDAO(db)
    expired_datetime = datetime.fromtimestamp(expired_time)
    await dao.end_expired_sessions(expired_datetime)
    return {"status": "Expired sessions processed"}
