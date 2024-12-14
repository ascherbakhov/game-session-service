from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app):
    instrumentator = Instrumentator()
    # instrumentator.add(lambda _: SESSIONS_CREATED)
    instrumentator.instrument(app).expose(app)
