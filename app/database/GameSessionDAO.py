from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException

from app.database.tables.models import GameSession

# SQLAlchemy setup

engine = create_engine("sqlite:///game_sessions.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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

    def update_heartbeat(self, session_id: int) -> GameSession:
        game_session = self.db_session.query(GameSession).filter(GameSession.id == session_id).first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Session not found")
        game_session.last_heartbeat = datetime.utcnow()
        self.db_session.commit()
        self.db_session.refresh(game_session)
        return game_session

    def end_expired_sessions(self):
        expired_time = datetime.utcnow() - timedelta(minutes=10)  # Assume session expires after 10 minutes of inactivity
        sessions = self.db_session.query(GameSession).filter(GameSession.session_end == None, GameSession.last_heartbeat < expired_time).all()
        for session in sessions:
            session.session_end = datetime.utcnow()
        self.db_session.commit()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()