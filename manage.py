import sys
from contextlib import contextmanager

from sqlalchemy.orm import Session
from uvicorn import run as uvicorn_run

from GameSessionDAO import Base, engine, SessionLocal
from expired_sessions import celery_app


# Manage.py script for managing FastAPI, Celery, and database setup

@contextmanager
def get_db_context() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def start_api():
    """Start the FastAPI server."""
    uvicorn_run("game_session_logger:app", host="127.0.0.1", port=8000, reload=True)

def start_celery_worker():
    """Start the Celery worker."""
    argv = [
        "worker",
        "--loglevel=info",
        "-Q",
        "celery",
    ]
    celery_app.worker_main(argv)

def start_celery_beat():
    """Start Celery Beat scheduler."""
    argv = [
        "beat",
        "--loglevel=info",
    ]
    celery_app.start(argv)

def reset_database():
    """Drop and recreate all database tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database has been reset.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [command]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start_api":
        start_api()
    elif command == "start_celery_worker":
        start_celery_worker()
    elif command == "start_celery_beat":
        start_celery_beat()
    elif command == "reset_db":
        reset_database()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
