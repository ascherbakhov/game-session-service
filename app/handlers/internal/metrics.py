from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

SESSIONS_CREATED = Counter("sessions_created_total", "Total number of created sessions")


async def setup_metrics(app):
    Instrumentator().instrument(app).add(lambda _: SESSIONS_CREATED).expose(app)
