from prometheus_client import REGISTRY, CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.handlers.game_session_logger import app


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
