from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.api.v1.dependencies import get_session_service
from app.api.v1.handlers.external.users import get_current_user
from app.api.v1.handlers.internal import metrics
from app.api.v1.schemas.session import StartSessionRequest, StopSessionRequest, HeartbeatResponse, StartSessionResponse, \
    EndSessionResponse
from app.core.config import app_config
from app.database.tables.models import User

game_session_router = APIRouter()


@game_session_router.post("/start/", response_model=StartSessionResponse, summary="Starting game session")
async def start_session(
    request: StartSessionRequest, session_service = Depends(get_session_service),
    current_user: User = Depends(get_current_user)
):
    result = await session_service.start_session(current_user, request.platform)
    metrics.SESSIONS_CREATED.inc()

    return result


@game_session_router.post(
    "/end/{session_id}", response_model=EndSessionResponse, summary="Ending game session"
)
async def end_session(
        request: StopSessionRequest, session_service = Depends(get_session_service),
        _=Depends(get_current_user)
):
    return await session_service.end_session(request.session_id)


@game_session_router.post(
    "/heartbeat/{session_id}",
    response_model=HeartbeatResponse,
    summary="Making heartbeat for game session",
    dependencies=[Depends(RateLimiter(times=2, seconds=app_config.expired_sessions_timeout))],
)
async def heartbeat(session_id: int, session_service = Depends(get_session_service), _=Depends(get_current_user)):
    return await session_service.heartbit(session_id)
