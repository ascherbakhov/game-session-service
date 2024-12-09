from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import app_config
from app.database.utils import init_engine
from app.handlers.external.game_sessions import game_session_router
from app.handlers.internal.game_sessions import internal_game_session_router
from app.handlers.limiter import init_rate_limiter, close_rate_limiter
from app.handlers.internal.metrics import setup_metrics
from app.handlers.external.users import users_router


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await init_rate_limiter()
    init_engine(app_config.database_url)
    yield app
    await close_rate_limiter()


def make_app():
    app = FastAPI(lifespan=app_lifespan)
    setup_metrics(app)
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(game_session_router, prefix="/api/v1")
    app.include_router(internal_game_session_router, prefix="/internal/v1")
    return app


app = make_app()
