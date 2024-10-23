from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends

from app.database.GameSessionDAO import GameSessionDAO, get_db

app = FastAPI()


# API endpoints
@app.post("/sessions/start/")
def start_session(user_id: str, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = dao.create_session(user_id)
    return {"session_id": session.id, "user_id": session.user_id, "session_start": session.session_start}

@app.post("/sessions/end/{session_id}")
def end_session(session_id: int, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = dao.end_session(session_id)
    return {"session_id": session.id, "user_id": session.user_id, "session_start": session.session_start, "session_end": session.session_end}

@app.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = dao.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.id, "user_id": session.user_id, "session_start": session.session_start, "session_end": session.session_end}

@app.post("/sessions/heartbeat/{session_id}")
def heartbeat(session_id: int, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = dao.update_heartbeat(session_id)
    return {"session_id": session.id, "user_id": session.user_id, "last_heartbeat": session.last_heartbeat}
