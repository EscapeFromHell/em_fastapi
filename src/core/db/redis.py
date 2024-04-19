from fastapi_cache import FastAPICache
from redis import asyncio as aioredis

redis = aioredis.from_url("redis://redis", encoding="utf8", decode_responses=True)
redis_cache = FastAPICache()
