from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import app_config
from app.database.dao.GameSessionDAO import GameSessionDAO
from app.database.tables.models import GameSession, User
from app.database.utils import get_db
from app.handlers.internal import metrics
from app.handlers.external.schemas import (
    StartSessionRequest,
    StopSessionRequest,
    HeartbeatResponse,
    StartSessionResponse,
    EndSessionResponse,
)
from app.handlers.external.users import get_current_user
from app.handlers.internal import redis_utls as redis_utils

game_session_router = APIRouter()


@game_session_router.post("/sessions/start/", response_model=StartSessionResponse, summary="Starting game session")
async def start_session(
    request: StartSessionRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    await redis_utils.invalidate_user_session_if_exists(current_user.username)

    dao = GameSessionDAO(db)
    game_session = GameSession(user_id=current_user.username, platform=request.platform)
    session = await dao.create_session(game_session)
    metrics.SESSIONS_CREATED.inc()

    session_data = {
        "session_id": session.id,
        "user_id": current_user.username,
        "session_start": session.session_start.isoformat(),
        "session_end": session.session_end
    }

    await redis_utils.save_session_to_cache(session.id, session_data)

    await redis_utils.set_current_session_for_user(current_user.username, session.id)

    return session_data


@game_session_router.post(
    "/sessions/end/{session_id}", response_model=EndSessionResponse, summary="Ending game session"
)
async def end_session(request: StopSessionRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await redis_utils.invalidate_user_session_if_exists(user.username)
    await redis_utils.delete_session_from_cache(request.session_id)

    dao = GameSessionDAO(db)
    session = await dao.end_session(request.session_id)
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "session_start": session.session_start,
        "session_end": session.session_end,
    }


@game_session_router.post(
    "/sessions/heartbeat/{session_id}",
    response_model=HeartbeatResponse,
    summary="Making heartbeat for game session",
    dependencies=[Depends(RateLimiter(times=2, seconds=app_config.expired_sessions_timeout))],
)
async def heartbeat(session_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    dao = GameSessionDAO(db)
    session = await dao.update_heartbeat(session_id)
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "last_heartbeat": session.last_heartbeat,
    }
