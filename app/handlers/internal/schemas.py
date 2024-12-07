from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GetSessionResponse(BaseModel):
    session_id: int
    user_id: str
    session_start: datetime
    session_end: Optional[datetime]
