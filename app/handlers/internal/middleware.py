from fastapi import HTTPException
from starlette.requests import Request

from app.config import app_config


async def verify_internal_access(request: Request):
    internal_token = request.headers.get("X-Internal-Token")
    if internal_token != app_config.internal_token:
        raise HTTPException(status_code=403, detail="Forbidden")
