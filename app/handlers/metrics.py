from prometheus_fastapi_instrumentator import Instrumentator
from app.handlers.main_app import app


Instrumentator().instrument(app).expose(app)
