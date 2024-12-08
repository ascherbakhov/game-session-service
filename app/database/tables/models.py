from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean
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


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    full_name = Column(String)
