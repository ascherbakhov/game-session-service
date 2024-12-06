from datetime import datetime, timedelta

from celery import Celery
from celery.schedules import crontab

from app.config import app_config
from app.database.dao.GameSessionDAO import GameSessionDAO
from app.database.utils import get_db

celery_app = Celery(__name__, broker="redis://redis_cache:6379/0")

celery_app.conf.beat_schedule = {
    "end-expired-sessions-every-10-minutes": {
        "task": "celery_end_expired_sessions",
        "schedule": crontab(minute="*/1"),  # Run every 1 minutes
    },
}
celery_app.conf.timezone = "UTC"


@celery_app.task
async def celery_end_expired_sessions():
    async for db in get_db():
        dao = GameSessionDAO(db)
        expired_time = datetime.now() - timedelta(minutes=app_config.expired_sessions_timeout)
        await dao.end_expired_sessions(expired_time)
        await db.close()
