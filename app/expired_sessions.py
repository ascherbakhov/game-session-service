from datetime import datetime, timedelta, timezone

from celery import Celery
from celery.schedules import crontab


from app.database.GameSessionDAO import AsyncSessionLocal, GameSessionDAO

# Celery setup
celery_app = Celery(__name__, broker='redis://localhost:6379/0')

# Celery Beat configuration to schedule periodic tasks
celery_app.conf.beat_schedule = {
    'end-expired-sessions-every-10-minutes': {
        'task': 'celery_end_expired_sessions',
        'schedule': crontab(minute='*/10'),  # Run every 10 minutes
    },
}
celery_app.conf.timezone = 'UTC'


# Celery task to automatically end expired sessions
@celery_app.task
async def celery_end_expired_sessions():
    db = AsyncSessionLocal()
    dao = GameSessionDAO(db)
    expired_time = datetime.now() - timedelta(minutes=10)
    await dao.end_expired_sessions(expired_time)
    db.close()
