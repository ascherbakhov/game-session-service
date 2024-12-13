from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import app_config
from app.core.database import init_engine, fini_engine
from app.api.v1.handlers.external.game_sessions import game_session_router
from app.api.v1.handlers.internal.game_sessions import internal_game_session_router
from app.api.v1.handlers.limiter import init_rate_limiter, close_rate_limiter
from app.api.v1.handlers.internal.metrics import setup_metrics
from app.api.v1.handlers.external.users import users_router


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await init_rate_limiter()
    init_engine(app_config.database_url)
    yield app
    fini_engine()
    await close_rate_limiter()


def make_app():
    app = FastAPI(lifespan=app_lifespan)
    setup_metrics(app)
    app.include_router(users_router, prefix="/api/v1/users")
    app.include_router(game_session_router, prefix="/api/v1/sessions")
    app.include_router(internal_game_session_router, prefix="/internal/v1")
    return app


app = make_app()
