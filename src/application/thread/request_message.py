from dataclasses import dataclass
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.message_gateway import MessageGateway
from src.application.common.usecase import Usecase
from src.domain.services.thread import ThreadService

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class RequestMessageInDTO:
    thread_id: UUID
    text: str


@dataclass(slots=True)
class RequestMessageOutDTO:
    answer: str


class RequestMessage(Usecase[RequestMessageInDTO, None]):
    """
    1. Get user's thread from state. If not presented, throw exception
    2. Get all user's context
    3. Send user's context to ai_model
    4. Return ai_model answer
    """
    def __init__(self, session: AsyncSession, message_gateway: MessageGateway, thread_service: ThreadService):
        self.session = session
        self.message_gateway = message_gateway
        self.thread_service = thread_service

    async def __call__(self, data: RequestMessageInDTO) -> RequestMessageOutDTO:
        await logger.ainfo(data.text)
        async with self.session.begin():
            context = await self.message_gateway.get_messages(data.thread_id)
            req = self.thread_service.create_request(data.thread_id, data.text)
            ctx = "\n".join([f"{msg.id} - {msg.text} - {msg.timestamp}" for msg in ([*context, req])])
            await logger.ainfo(ctx)
            await self.message_gateway.create_message(req)

            # response = await self.ai_adapter.request(req.text)
            res = self.thread_service.create_response(req.id, data.text)
            await self.message_gateway.create_response(res)

            return RequestMessageOutDTO(answer=res.text)
