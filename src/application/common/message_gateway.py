from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID

from src.domain.models.thread import RequestMessage, ResponseMessage


class MessageGateway(ABC):
    @abstractmethod
    async def create_message(self, request: RequestMessage) -> None:
        pass

    @abstractmethod
    async def create_response(self, response: ResponseMessage) -> None:
        pass

    @abstractmethod
    async def get_messages(self, thread_id: UUID) -> Sequence[RequestMessage | ResponseMessage]:
        pass
