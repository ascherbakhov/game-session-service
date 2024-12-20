from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import app_config
from app.core.database import init_engine, fini_engine
from app.handlers.api.v1.api_spec.game_sessions import game_session_router
from app.handlers.internal.v1.api_spec.game_sessions import internal_game_session_router
from app.core.limiter import init_rate_limiter, close_rate_limiter
from app.core.middlewares.metrics_middleware import setup_metrics
from app.handlers.api.v1.api_spec.users import auth_router
from app.core.redis import init_redis, fini_redis


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    init_redis(app_config.redis.url)
    await init_rate_limiter()
    init_engine(app_config.database_url)
    yield
    fini_engine()
    await close_rate_limiter()
    await fini_redis()


def make_app():
    app = FastAPI(lifespan=app_lifespan)
    setup_metrics(app)
    app.include_router(auth_router, prefix="/api/v1/auth")
    app.include_router(game_session_router, prefix="/api/v1/sessions")
    app.include_router(internal_game_session_router, prefix="/internal/v1")
    return app


app = make_app()
