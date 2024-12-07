from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from app.database.utils import get_db
from app.database.dao.GameSessionDAO import GameSessionDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.internal.utils import get_session_from_cache, save_session_to_cache
from app.handlers.internal.middleware import verify_internal_access

internal_game_session_router = APIRouter(dependencies=[Depends(verify_internal_access)])


@internal_game_session_router.get("/sessions/{session_id}")
async def get_session_internal(session_id: int, db: AsyncSession = Depends(get_db)):
    session_data = await get_session_from_cache(session_id)
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

    await save_session_to_cache(session_id, session_data)
    return session_data


@internal_game_session_router.delete("/sessions/end_expired")
async def end_expired(expired_time: int, db: AsyncSession = Depends(get_db)):
    dao = GameSessionDAO(db)
    expired_datetime = datetime.fromtimestamp(expired_time).replace(tzinfo=timezone.utc)
    await dao.end_expired_sessions(expired_datetime)
    return {"status": "Expired sessions processed"}
