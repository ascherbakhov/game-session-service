from celery import Celery

from GameSessionDAO import SessionLocal, GameSessionDAO

# Celery setup
celery_app = Celery(__name__, broker='redis://localhost:6379/0')


# Celery task to automatically end expired sessions
@celery_app.task
def celery_end_expired_sessions():
    db = SessionLocal()
    dao = GameSessionDAO(db)
    dao.end_expired_sessions()
    db.close()
