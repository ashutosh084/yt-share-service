import aioredis
import os

def get_cache():
    if os.getenv("REDIS_URL"):
        redis = aioredis.from_url(os.getenv("REDIS_URL"))
    else:
        redis = aioredis.from_url("redis://localhost")
    return redis

cache = aioredis.from_url("redis://localhost")

async def get_from_cache(key):
    return await cache.get(key)

async def save_to_cache(key, value):
    await cache.set(key, value)