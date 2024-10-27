from pydantic import BaseModel

class StartSessionRequest(BaseModel):
    user_id: str
    platform: str

class StopSessionRequest(BaseModel):
    session_id: int
