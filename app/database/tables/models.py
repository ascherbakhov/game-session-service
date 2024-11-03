from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    platform = Column(String, index=True, nullable=True)
    session_start = Column(DateTime, default=lambda: datetime.now())
    session_end = Column(DateTime, nullable=True)
    last_heartbeat = Column(DateTime, default=lambda: datetime.now())
