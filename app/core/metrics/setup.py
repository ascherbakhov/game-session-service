from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

SESSIONS_CREATED = Counter("sessions_created_total", "Total number of created sessions")


def setup_metrics(app):
    instrumentator = Instrumentator()
    # instrumentator.add(lambda _: SESSIONS_CREATED)
    instrumentator.instrument(app).expose(app)
