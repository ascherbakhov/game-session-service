from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StartSessionRequest(BaseModel):
    platform: str


class StopSessionRequest(BaseModel):
    session_id: int


class HeartbeatResponse(BaseModel):
    session_id: int
    user_id: str
    last_heartbeat: datetime


class StartSessionResponse(BaseModel):
    session_id: int
    user_id: str
    session_start: datetime


class EndSessionResponse(BaseModel):
    session_id: int
    user_id: str
    session_start: datetime
    session_end: Optional[datetime]


class GetSessionResponse(BaseModel):
    session_id: int
    user_id: str
    session_start: datetime
    session_end: Optional[datetime]


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = None
