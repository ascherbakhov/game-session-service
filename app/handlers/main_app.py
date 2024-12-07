from fastapi import FastAPI

from app.handlers.external.game_sessions import game_session_router
from app.handlers.internal.game_sessions import internal_game_session_router
from app.handlers.limiter import init_rate_limiter, close_rate_limiter
from app.handlers.internal.metrics import setup_metrics
from app.handlers.external.users import users_router

app = FastAPI()
setup_metrics(app)


@app.on_event("startup")
async def startup():
    await init_rate_limiter()


@app.on_event("shutdown")
async def shutdown():
    await close_rate_limiter()


app.include_router(users_router, prefix="/api/v1")
app.include_router(game_session_router, prefix="/api/v1")
app.include_router(internal_game_session_router, prefix="/internal/v1")
