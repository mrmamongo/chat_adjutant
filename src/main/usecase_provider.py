from typing import AsyncIterable

from aiogram import Bot, Dispatcher
from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.bot.dispatch_update import DispatchUpdate
from src.application.common.hello_message import HelloMessageType
from src.application.common.message_gateway import MessageGateway
from src.application.common.thread_gateway import ThreadGateway
from src.application.common.user_gateway import UserGateway
from src.application.thread.request_message import RequestMessage
from src.application.user.init_user import InitUser
from src.domain.services.thread import ThreadService
from src.domain.services.user import UserService


class UsecaseProvider(Provider):
    # @provide(scope=Scope.REQUEST)
    # async def get_get_all_threads(
    #     self, thread_gateway: ThreadGateway
    # ) -> AsyncIterable[GetAllThreads]:
    #     yield GetAllThreads(thread_gateway)

    @provide(scope=Scope.REQUEST)
    async def get_init_user(self, hello_message: HelloMessageType, session: AsyncSession, user_gateway: UserGateway,
                            user_service: UserService, thread_service: ThreadService,
                            thread_gateway: ThreadGateway, ) -> AsyncIterable[InitUser]:
        yield InitUser(hello_message, session, user_gateway, user_service, thread_gateway, thread_service, )

    @provide(scope=Scope.REQUEST)
    async def get_dispatch_update(self, bot: Bot, dp: Dispatcher) -> AsyncIterable[DispatchUpdate]:
        yield DispatchUpdate(bot=bot, dp=dp)

    @provide(scope=Scope.REQUEST)
    async def get_request_message(self, session: AsyncSession, message_gateway: MessageGateway,
                                  thread_service: ThreadService) -> AsyncIterable[RequestMessage]:
        yield RequestMessage(session, message_gateway, thread_service)
