import os
import aioredis
from dotenv import load_dotenv

load_dotenv()

redis_client = aioredis.from_url(os.getenv("REDIS_URL"))

async def get_from_cache(key):
    return await redis_client.get(key)

async def save_to_cache(key, value):
    await redis_client.set(key, value)
