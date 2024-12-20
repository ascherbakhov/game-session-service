from fastapi import APIRouter, Depends, HTTPException

from app.core.logging import session_logger
from app.handlers.dependencies import get_session_service, verify_internal_access
from app.DTOs.game_session import SessionDTO

internal_game_session_router = APIRouter(dependencies=[Depends(verify_internal_access)])


@internal_game_session_router.get("/sessions/{session_id}", response_model=SessionDTO)
async def get_session_internal(session_id: int, session_service=Depends(get_session_service)):
    session_dto = await session_service.get_session(session_id)
    if not session_dto:
        raise HTTPException(404, "Session not found")

    return session_dto


@internal_game_session_router.get("/users/{user_id}/sessions/current", response_model=SessionDTO)
async def get_current_session_for_user(user_id: str, session_service=Depends(get_session_service)):
    session_data = await session_service.get_session_by_user(user_id)
    if not session_data:
        raise HTTPException(404, "Session not found")

    return session_data


@internal_game_session_router.post("/sessions/end_expired")
async def end_expired(session_service=Depends(get_session_service)):
    try:
        await session_service.end_expired_sessions()
    except Exception as exc:
        session_logger.exception(f"Generic error occured while ending expired sessions {exc}")
        raise HTTPException(500)
    return {"status": "Expired sessions processed"}
