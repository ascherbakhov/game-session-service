from datetime import datetime, timezone

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao.GameSessionDAO import GameSessionDAO
from app.database.tables.User import User
from app.database.tables.models import GameSession
from app.database.utils import get_db
from app.handlers.schemas import (
    EndSessionResponse,
    GetSessionResponse,
    HeartbeatResponse,
    StartSessionRequest,
    StartSessionResponse,
    StopSessionRequest,
)
from app.handlers.users import get_current_user

v1_router = APIRouter()


@v1_router.post("/sessions/start/", response_model=StartSessionResponse, summary="Starting game session")
async def start_session(
    request: StartSessionRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    dao = GameSessionDAO(db)
    game_session = GameSession(user_id=current_user.username, platform=request.platform)
    session = await dao.create_session(game_session)
    return {
        "session_id": session.id,
        "user_id": current_user.username,
        "session_start": session.session_start,
    }


@v1_router.post("/sessions/end/{session_id}", response_model=EndSessionResponse, summary="Ending game session")
async def end_session(request: StopSessionRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    dao = GameSessionDAO(db)
    session = await dao.end_session(request.session_id)
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "session_start": session.session_start,
        "session_end": session.session_end,
    }


@v1_router.get("/sessions/{session_id}", response_model=GetSessionResponse, summary="Getting game session")
async def get_session(session_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    dao = GameSessionDAO(db)
    session = await dao.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "session_start": session.session_start,
        "session_end": session.session_end,
    }


@v1_router.post(
    "/sessions/heartbeat/{session_id}", response_model=HeartbeatResponse, summary="Making heartbeat for game session"
)
async def heartbeat(session_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    dao = GameSessionDAO(db)
    session = await dao.update_heartbeat(session_id)
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "last_heartbeat": session.last_heartbeat,
    }


@v1_router.delete("/sessions/end_expired")
async def end_expired(expired_time: int, db: AsyncSession = Depends(get_db)):
    dao = GameSessionDAO(db)
    expired_datetime = datetime.fromtimestamp(expired_time).replace(tzinfo=timezone.utc)
    await dao.end_expired_sessions(expired_datetime)
    return {"status": "Expired sessions processed"}
