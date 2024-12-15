import redis


redis_client = None


def init_redis(redis_url):
    global redis_client
    redis_client = redis.asyncio.from_url(redis_url, encoding="utf-8", decode_responses=True)


async def fini_redis():
    global redis_client
    await redis_client.aclose()


def get_cache():
    return redis_client
