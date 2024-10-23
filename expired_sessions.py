from celery import Celery
from celery.schedules import crontab


from GameSessionDAO import SessionLocal, GameSessionDAO

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
def celery_end_expired_sessions():
    db = SessionLocal()
    dao = GameSessionDAO(db)
    dao.end_expired_sessions()
    db.close()
