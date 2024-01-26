from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.hello_message import HelloMessageType
from src.application.common.thread_gateway import ThreadGateway
from src.application.common.usecase import Usecase
from src.application.common.user_gateway import UserGateway
from src.domain.models.thread import Thread
from src.domain.models.user import User
from src.domain.services.thread import ThreadService
from src.domain.services.user import UserService


@dataclass(slots=True)
class InitUserInDTO:
    user_id: str
    username: str


@dataclass(slots=True)
class InitUserOutDTO:
    thread_id: UUID
    hello_message: HelloMessageType


class InitUser(Usecase[InitUserInDTO, InitUserOutDTO]):
    """
    1. Register User in database if not already registered
    2. Get user thread from database. If not presented, create new. Get thread id
    3. Set thread id as FSM data
    4. Send hello message
    """

    def __init__(
        self,
        hello_message: HelloMessageType,
        session: AsyncSession,
        user_gateway: UserGateway,
        user_service: UserService,
        thread_gateway: ThreadGateway,
        thread_service: ThreadService,
    ) -> None:
        self.hello_message = hello_message  # TODO: сделать наверное настраиваемым
        self.session = session
        self.user_gateway = user_gateway
        self.user_service = user_service
        self.thread_gateway = thread_gateway
        self.thread_service = thread_service

    async def __call__(self, data: InitUserInDTO) -> InitUserOutDTO:
        async with self.session.begin():
            user: User
            if await self.user_gateway.check_exists(data.user_id):
                user = await self.user_gateway.get_by_telegram_id(data.user_id)
            else:
                user = self.user_service.create_user(data.user_id, data.username)
                await self.user_gateway.create(user)

            thread: Thread
            if await self.thread_gateway.check_exists(user.id):
                thread = await self.thread_gateway.get_by_user_id(user.id)
            else:
                thread = self.thread_service.create_thread(user.id)
                await self.thread_gateway.create(thread)

        return InitUserOutDTO(thread_id=thread.id, hello_message=self.hello_message)
