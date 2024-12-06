from datetime import datetime, timedelta

from celery import Celery
from celery.schedules import crontab

from app.database.dao.GameSessionDAO import GameSessionDAO
from app.database.utils import get_db

# Celery setup
celery_app = Celery(__name__, broker="redis://localhost:6379/0")

# Celery Beat configuration to schedule periodic tasks
celery_app.conf.beat_schedule = {
    "end-expired-sessions-every-10-minutes": {
        "task": "celery_end_expired_sessions",
        "schedule": crontab(minute="*/10"),  # Run every 10 minutes
    },
}
celery_app.conf.timezone = "UTC"


# Celery task to automatically end expired sessions
@celery_app.task
async def celery_end_expired_sessions():
    async for db in get_db():
        dao = GameSessionDAO(db)
        expired_time = datetime.now() - timedelta(minutes=10)
        await dao.end_expired_sessions(expired_time)
        await db.close()
