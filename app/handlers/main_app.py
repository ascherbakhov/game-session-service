from fastapi import FastAPI

from app.handlers.game_session_logger import game_session_router
from app.handlers.limiter import init_rate_limiter, close_rate_limiter
from app.handlers.metrics import setup_metrics
from app.handlers.users import users_router

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_rate_limiter()
    await setup_metrics(app)


@app.on_event("shutdown")
async def shutdown():
    await close_rate_limiter()


app.include_router(users_router, prefix="/api/v1")
app.include_router(game_session_router, prefix="/api/v1")
