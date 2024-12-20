from typing import Optional

from pydantic import BaseModel

from app.database.tables.models import GameSession


class HeartbeatDTO(BaseModel):
    session_id: int
    user_id: str
    last_heartbeat: str


class SessionDTO(BaseModel):
    session_id: int
    user_id: str
    session_start: str
    session_end: Optional[str]

    @staticmethod
    def create_by_session(session: GameSession):
        return SessionDTO(
            session_id=session.id,
            user_id=session.user_id,
            session_start=session.session_start_iso,
            session_end=session.session_end_iso,
        )
