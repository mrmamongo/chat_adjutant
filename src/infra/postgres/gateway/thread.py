from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from src.application.common.thread_gateway import ThreadGateway
from src.domain.models.thread import Thread
from src.infra.postgres.exception import GatewayException
from src.infra.postgres.gateway.base import SAGateway
from src.infra.postgres.models import ThreadModel


def convert_db_to_domain(db_model: ThreadModel) -> Thread:
    return Thread(
        id=db_model.id,
        user_id=db_model.user_id,
    )


def convert_domain_to_db(thread: Thread) -> ThreadModel:
    return ThreadModel(
        id=thread.id,
        user_id=thread.user_id,
    )


class SAThreadGateway(SAGateway, ThreadGateway):
    async def check_exists(self, user_id: UUID) -> bool:
        exists = (
            await self.session.execute(
                select(
                    select(ThreadModel).where(ThreadModel.user_id == user_id).exists()
                )
            )
        ).one_or_none()
        return exists is not None and exists[0]

    async def get_by_user_id(self, user_id: UUID) -> Thread:
        model: ThreadModel = (
            await self.session.scalars(
                select(ThreadModel).where(ThreadModel.user_id == user_id).limit(1)
            )
        ).one_or_none()
        return convert_db_to_domain(model)

    async def create(self, thread: Thread) -> None:
        model = convert_domain_to_db(thread)

        try:
            self.session.add(model)
            await self.session.flush()
        except DBAPIError as e:
            self._parse_exc(e, thread)

    @staticmethod
    def _parse_exc(err: DBAPIError, thread: Thread) -> NoReturn:
        match err.__cause__.__cause__.constraint_name:  # type: ignore
            case _:
                raise GatewayException from err
