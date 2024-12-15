from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StartSessionRequest(BaseModel):
    platform: str


class StopSessionRequest(BaseModel):
    session_id: int


class HeartbeatDTO(BaseModel):
    session_id: int
    user_id: str
    last_heartbeat: str


class SessionDTO(BaseModel):
    session_id: int
    user_id: str
    session_start: str
    session_end: Optional[str]
