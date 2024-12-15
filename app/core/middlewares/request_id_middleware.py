import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import session_logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        session_logger.info(f"[RequestID={request_id}] {request.method} {request.url}")

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        session_logger.debug(f"[RequestID={request_id}] response={response}")

        return response
