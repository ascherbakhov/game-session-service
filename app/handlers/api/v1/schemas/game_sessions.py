from enum import StrEnum

from pydantic import BaseModel


class PlatformEnum(StrEnum):
    linux = "Linux"
    windows = "Windows"
    macos = "MacOS"


class StartSessionRequest(BaseModel):
    platform: PlatformEnum


class StopSessionRequest(BaseModel):
    session_id: int
