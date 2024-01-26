from abc import ABC, abstractmethod

from src.domain.models.user import User


class UserGateway(ABC):
    @abstractmethod
    async def check_exists(self, telegram_id: str) -> bool:
        pass

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: str) -> User:
        pass

    @abstractmethod
    async def create(self, user: User) -> None:
        pass
