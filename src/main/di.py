from typing import AsyncIterable

import structlog
from aiogram import Bot, Dispatcher
from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.templating import Jinja2Templates

from src.application.common.ai_adapter import AIAdapter
from src.application.common.hello_message import HelloMessageType
from src.application.common.message_gateway import MessageGateway
from src.application.common.thread_gateway import ThreadGateway
from src.application.common.user_gateway import UserGateway
from src.config import Config
from src.domain.services.thread import ThreadService
from src.domain.services.user import UserService
from src.infra.gemini.adapter import GeminiAIAdapter
from src.infra.postgres.gateway.message import SAMessageGateway
from src.infra.postgres.gateway.thread import SAThreadGateway
from src.infra.postgres.gateway.user import SAUserGateway

logger = structlog.get_logger(__name__)


class DIProvider(Provider):
    def __init__(self, config: Config, dispatcher: Dispatcher, bot: Bot):
        super().__init__()
        self.config = config
        self.dispatcher = dispatcher
        self.bot = bot

    @provide(scope=Scope.APP)
    async def get_hello_message(self) -> AsyncIterable[HelloMessageType]:
        yield HelloMessageType(self.config.telegram.hello_message)

    @provide(scope=Scope.APP)
    async def get_engine(self) -> AsyncIterable[AsyncEngine]:
        engine: AsyncEngine = create_async_engine(self.config.database.dsn)
        yield engine

        await engine.dispose()

    @provide(scope=Scope.APP)
    async def get_bot(self) -> AsyncIterable[Bot]:
        yield self.bot

    @provide(scope=Scope.APP)
    async def get_dp(self) -> AsyncIterable[Dispatcher]:
        yield self.dispatcher

    @provide(scope=Scope.APP)
    async def get_session_maker(
        self, engine: AsyncEngine
    ) -> AsyncIterable[async_sessionmaker]:
        yield async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    #
    # @provide(scope=Scope.APP)
    # async def get_jinja_templates(self) -> AsyncIterable[Jinja2Templates]:
    #     yield Jinja2Templates(self.config.api.templates_dir)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_thread_service(self) -> AsyncIterable[ThreadService]:
        yield ThreadService()

    @provide(scope=Scope.REQUEST)
    async def get_thread_gateway(
        self, session: AsyncSession
    ) -> AsyncIterable[ThreadGateway]:
        yield SAThreadGateway(session)

    @provide(scope=Scope.REQUEST)
    async def get_user_service(self) -> AsyncIterable[UserService]:
        yield UserService()

    @provide(scope=Scope.REQUEST)
    async def get_user_gateway(
        self, session: AsyncSession
    ) -> AsyncIterable[UserGateway]:
        yield SAUserGateway(session)

    @provide(scope=Scope.REQUEST)
    async def get_message_gateway(self, session: AsyncSession
                                  ) -> AsyncIterable[MessageGateway]:
        yield SAMessageGateway(session)

    @provide(scope=Scope.REQUEST)
    async def get_ai_service(self) -> AsyncIterable[AIAdapter]:
        yield GeminiAIAdapter()
