from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends

from app.database.GameSessionDAO import GameSessionDAO, get_db
from app.handlers.validation import StartSessionRequest, StopSessionRequest, HeartbitRequest

app = FastAPI()


# API endpoints
@app.post("/sessions/start/")
async def start_session(request: StartSessionRequest, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = await dao.create_session(request.user_id)
    return {"session_id": session.id, "user_id": session.user_id, "session_start": session.session_start}

@app.post("/sessions/end/{session_id}")
async def end_session(request: StopSessionRequest, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = await dao.end_session(request.session_id)
    return {"session_id": session.id, "user_id": session.user_id, "session_start": session.session_start, "session_end": session.session_end}

@app.get("/sessions/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = await dao.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.id, "user_id": session.user_id, "session_start": session.session_start, "session_end": session.session_end}

@app.post("/sessions/heartbeat/{session_id}")
async def heartbeat(session_id: int, db: Session = Depends(get_db)):
    dao = GameSessionDAO(db)
    session = await dao.update_heartbeat(session_id)
    return {"session_id": session.id, "user_id": session.user_id, "last_heartbeat": session.last_heartbeat}
