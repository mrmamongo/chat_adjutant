from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models.thread import Thread


class ThreadGateway(ABC):
    @abstractmethod
    async def check_exists(self, user_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Thread:
        pass

    @abstractmethod
    async def create(self, thread: Thread) -> None:
        pass
