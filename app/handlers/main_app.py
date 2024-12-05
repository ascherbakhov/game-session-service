from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.handlers.game_session_logger import v1_router
from app.handlers.users import users_router

app = FastAPI()

app.include_router(users_router, prefix='/api/v1')
app.include_router(v1_router, prefix='/api/v1')
Instrumentator().instrument(app).expose(app)
