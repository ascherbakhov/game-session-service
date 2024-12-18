from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class PlatformEnum(StrEnum):
    linux = "Linux"
    windows = "Windows"
    macos = "MacOS"


class StartSessionRequest(BaseModel):
    platform: PlatformEnum


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
