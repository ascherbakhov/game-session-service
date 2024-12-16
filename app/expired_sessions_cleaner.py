import asyncio

from celery import Celery
from celery.schedules import crontab

from app.api.v1.dependencies import get_session_service
from app.core.config import app_config
from app.core.database import get_db, init_engine
from app.core.redis import get_cache

celery_app = Celery(__name__, broker=app_config.redis_url)

celery_app.conf.beat_schedule = {
    "end-expired-sessions-every-10-minutes": {
        "task": "celery_end_expired_sessions",
        "schedule": crontab(minute="*/1"),  # Run every 1 minutes
    },
}
celery_app.conf.timezone = "UTC"
init_engine(app_config.database_url)


@celery_app.task(name="celery_end_expired_sessions")
def celery_end_expired_sessions():
    async def get_session():
        session = await anext(get_db())
        return session

    db = asyncio.run(get_session())
    cache = get_cache()
    session_service = get_session_service(db=db, cache=cache)
    asyncio.run(session_service.end_expired_sessions())
