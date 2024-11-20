from uvicorn import run as uvicorn_run

from app.expired_sessions import celery_app

# Manage.py script for managing FastAPI, Celery, and database setup


def start_api():
    """Start the FastAPI server."""
    uvicorn_run("app.handlers.game_session_logger:app", host="127.0.0.1", port=8000, reload=True)


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
