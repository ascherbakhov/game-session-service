from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_session_service, verify_internal_access

internal_game_session_router = APIRouter(dependencies=[Depends(verify_internal_access)])


@internal_game_session_router.get("/sessions/{session_id}")
async def get_session_internal(session_id: int, session_service=Depends(get_session_service)):
    return await session_service.get_session(session_id)


@internal_game_session_router.delete("/sessions/end_expired")
async def end_expired(session_service=Depends(get_session_service)):
    await session_service.end_expired_sessions()
    return {"status": "Expired sessions processed"}
