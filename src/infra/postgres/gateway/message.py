import datetime
from typing import NoReturn, Sequence
from uuid import UUID

import structlog
from adaptix import as_is_loader, name_mapping, Retort
from sqlalchemy import select, union
from sqlalchemy.exc import DBAPIError

from src.application.common.message_gateway import MessageGateway
from src.domain.models.thread import Message, RequestMessage, ResponseMessage
from src.infra.postgres.exception import GatewayException
from src.infra.postgres.gateway.base import SAGateway
from src.infra.postgres.models import RequestMessageModel, ResponseMessageModel


def req_convert_db_to_domain(db_model: RequestMessageModel) -> RequestMessage:
    return RequestMessage(thread_id=db_model.thread_id, text=db_model.text, id=db_model.id,
                          timestamp=db_model.timestamp)


def req_convert_domain_to_db(request: RequestMessage) -> RequestMessageModel:
    return RequestMessageModel(thread_id=request.thread_id, text=request.text, id=request.id,
                               timestamp=request.timestamp)


def res_convert_db_to_domain(db_model: ResponseMessageModel) -> ResponseMessage:
    return ResponseMessage(text=db_model.text, message_id=db_model.id, timestamp=db_model.timestamp)


def res_convert_domain_to_db(response: ResponseMessage) -> ResponseMessageModel:
    return ResponseMessageModel(text=response.text, id=response.message_id, timestamp=response.timestamp)


class SAMessageGateway(SAGateway, MessageGateway):
    retort = Retort(recipe=[name_mapping(Message, as_list=True), as_is_loader(datetime.datetime), as_is_loader(UUID)])

    async def create_message(self, request: RequestMessage) -> None:
        model = req_convert_domain_to_db(request)

        try:
            self.session.add(model)
            await self.session.flush()
        except DBAPIError as e:
            self._parse_exc(e)

    async def create_response(self, response: ResponseMessage) -> None:
        model = res_convert_domain_to_db(response)

        try:
            self.session.add(model)
            await self.session.flush()
        except DBAPIError as e:
            self._parse_exc(e)

    async def get_messages(self, thread_id: UUID) -> Sequence[Message]:
        stmt = union(select(RequestMessageModel.id, RequestMessageModel.text, RequestMessageModel.timestamp),
                     select(ResponseMessageModel.id, ResponseMessageModel.text,
                            ResponseMessageModel.timestamp)).order_by(RequestMessageModel.timestamp).order_by(
            ResponseMessageModel.timestamp)
        await structlog.get_logger(__name__).ainfo(stmt)
        seq = (await self.session.execute(stmt)).fetchall()
        await structlog.get_logger(__name__).ainfo(seq)

        return self.retort.load(seq, Sequence[Message])

    @staticmethod
    def _parse_exc(err: DBAPIError) -> NoReturn:
        match err.__cause__.__cause__.constraint_name:  # type: ignore
            case _:
                raise GatewayException from err
