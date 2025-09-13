# Dependency injection setup
import asyncpg
import redis.asyncio as redis
from fastapi import Depends

from core.config import settings


async def get_pg_pool():
    return await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=2, max_size=20)


async def get_redis():
    return redis.Redis(host="localhost", port=6379, decode_responses=True)


async def get_db(conn: asyncpg.Pool = Depends(get_pg_pool)):
    async with conn.acquire() as connection:
        yield connection
