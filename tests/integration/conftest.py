from unittest.mock import AsyncMock, patch

import pytest
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from httpx import AsyncClient
from starlette.responses import JSONResponse

from app.database.utils import get_db
from tests.factories import UserFactory, TEST_PASSWORD


@pytest.fixture(scope="module", autouse=True)
def mock_fastapi_limiter():
    with patch("fastapi_limiter.FastAPILimiter.init", new_callable=AsyncMock), \
            patch("fastapi_limiter.FastAPILimiter.close", new_callable=AsyncMock):
        FastAPILimiter.redis = AsyncMock()
        FastAPILimiter.redis.get = AsyncMock(return_value=None)
        FastAPILimiter.redis.set = AsyncMock(return_value=True)
        FastAPILimiter.redis.incr = AsyncMock(return_value=1)
        FastAPILimiter.redis.delete = AsyncMock(return_value=True)
        FastAPILimiter.redis.evalsha = AsyncMock(return_value=0)

        async def mock_identifier(request):
            return "test-identifier"

        FastAPILimiter.identifier = mock_identifier
        async def mock_http_callback(request, response, pexpire):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "retry_after": pexpire / 1000},
            )

        FastAPILimiter.http_callback = mock_http_callback
        yield

@pytest.fixture(scope="module", autouse=True)
async def test_client():
    from app.handlers.main_app import app
    await app.router.startup()
    client = AsyncClient(app=app, base_url="http://test")
    rate_limiter_mock = AsyncMock(spec=RateLimiter)
    app.dependency_overrides[RateLimiter] = lambda: rate_limiter_mock
    return client


@pytest.fixture
async def async_client(test_client):
    yield test_client


@pytest.fixture
async def test_user():
    async_session = await anext(get_db())

    user = await UserFactory.create(session=async_session)
    return user


@pytest.fixture
async def user_token(test_user, async_client):
    response = await async_client.post(
        "/api/v1/token",
        data={"username": test_user.username, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
