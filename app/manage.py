from uvicorn import run as uvicorn_run

from app.api.v1.handlers import celery_app
from app.core.config import app_config


# Manage.py script for managing FastAPI, Celery, and database setup


def start_api():
    """Start the FastAPI server."""
    uvicorn_run("app.handlers.main_app:app", host="127.0.0.1", port=8000, reload=True)


def start_celery_worker():
    """Start the Celery worker."""
    argv = [
        "worker",
        f"--loglevel={"info" if not app_config.debug else "debug"}",
        "-Q",
        "celery",
    ]
    celery_app.worker_main(argv)


def start_celery_beat():
    """Start Celery Beat scheduler."""
    argv = [
        "beat",
        f"--loglevel={"info" if not app_config.debug else "debug"}",
    ]
    celery_app.start(argv)
