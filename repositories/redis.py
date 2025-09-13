# Redis database operations

from typing import Optional

import redis.asyncio as redis

from repositories.base import BaseStorage


class RedisStorage(BaseStorage):
    def __init__(self, client: redis.Redis):
        self.client = client

    async def store(self, key: str, data: str, ex: int) -> bool:
        await self.client.set(key, data, ex=ex)
        return True

    async def retrieve(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    # Resto...
