from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.api.v1.dependencies import get_session_service, get_current_user
from app.api.v1.DTOs.game_session import StartSessionRequest, StopSessionRequest, HeartbeatDTO, SessionDTO
from app.core.config import app_config
from app.core.metrics import prometheus_metrics

game_session_router = APIRouter()


@game_session_router.post("/start/", response_model=SessionDTO, summary="Starting game session")
async def start_session(
    request: StartSessionRequest,
    session_service=Depends(get_session_service),
    current_user=Depends(get_current_user),
):
    result = await session_service.start_session(current_user, request.platform)
    prometheus_metrics.SESSIONS_CREATED.inc()

    return dict(result)


@game_session_router.post("/end/{session_id}", response_model=SessionDTO, summary="Ending game session")
async def end_session(
    request: StopSessionRequest, session_service=Depends(get_session_service), _=Depends(get_current_user)
):
    result = await session_service.end_session(request.session_id)
    return dict(result)


@game_session_router.post(
    "/heartbeat/{session_id}",
    response_model=HeartbeatDTO,
    summary="Making heartbeat for game session",
    dependencies=[Depends(RateLimiter(times=2, seconds=app_config.expired_sessions_timeout))],
)
async def heartbeat(session_id: int, session_service=Depends(get_session_service), _=Depends(get_current_user)):
    result = await session_service.heartbit(session_id)
    return dict(result)
