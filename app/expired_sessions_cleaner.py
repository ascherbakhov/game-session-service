import asyncio

from celery import Celery
from celery.schedules import crontab

from app.handlers.dependencies import get_session_service
from app.core.config import app_config
from app.core.database import init_engine, get_session_maker
from app.core.logging import session_logger
from app.core.redis import get_cache

celery_app = Celery(__name__, broker=app_config.redis.url)

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
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_until_complete(_end_expired_sessions())
        else:
            loop.create_task(_end_expired_sessions())
    except Exception as e:
        session_logger.exception(f"Error in Celery task: {e}")


async def _end_expired_sessions():
    async_session_maker = get_session_maker()
    async with async_session_maker() as db:
        cache = get_cache()
        session_service = get_session_service(db=db, cache=cache)

        await session_service.end_expired_sessions()
