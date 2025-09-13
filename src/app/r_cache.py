from config import REDIS_CACHE_DB, REDIS_HOST, REDIS_PORT
from redis import asyncio as aioredis


async def get_redis_client():

    redis_client = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_CACHE_DB)
    try:
        yield redis_client
    finally:
        await redis_client.close()
