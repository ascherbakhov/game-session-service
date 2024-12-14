from celery import Celery
from celery.schedules import crontab

from app.api.v1.dependencies import get_session_service
from app.core.config import app_config

celery_app = Celery(__name__, broker=app_config.redis_url)

celery_app.conf.beat_schedule = {
    "end-expired-sessions-every-10-minutes": {
        "task": "celery_end_expired_sessions",
        "schedule": crontab(minute="*/1"),  # Run every 1 minutes
    },
}
celery_app.conf.timezone = "UTC"


@celery_app.task
async def celery_end_expired_sessions():
    session_service = get_session_service()
    await session_service.end_expired_sessions()
