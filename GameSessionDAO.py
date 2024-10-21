from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import HTTPException

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine("sqlite:///game_sessions.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database model for GameSession
class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime, nullable=True)


# DAO for accessing game session data
class GameSessionDAO:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_session(self, user_id: str) -> GameSession:
        game_session = GameSession(user_id=user_id)
        self.db_session.add(game_session)
        self.db_session.commit()
        self.db_session.refresh(game_session)
        return game_session

    def end_session(self, session_id: int) -> GameSession:
        game_session = self.db_session.query(GameSession).filter(GameSession.id == session_id).first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Session not found")
        game_session.session_end = datetime.utcnow()
        self.db_session.commit()
        self.db_session.refresh(game_session)
        return game_session

    def get_session(self, session_id: int) -> Optional[GameSession]:
        return self.db_session.query(GameSession).filter(GameSession.id == session_id).first()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()