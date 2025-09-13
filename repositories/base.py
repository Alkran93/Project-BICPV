# Base repository interface

from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    async def store(self, data: dict) -> bool:
        pass

    @abstractmethod
    async def retrieve(self, query: str) -> list[dict]:
        pass

    # Resto: delete, etc.
