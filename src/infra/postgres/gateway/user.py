from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from src.application.common.user_gateway import UserGateway
from src.domain.models.user import User
from src.infra.postgres.exception import GatewayException
from src.infra.postgres.gateway.base import SAGateway
from src.infra.postgres.models import UserModel


def convert_db_to_domain(db_model: UserModel) -> User:
    return User(
        id=db_model.id, telegram_id=db_model.telegram_id, username=db_model.username
    )


def convert_domain_to_db(user: User) -> UserModel:
    return UserModel(id=user.id, username=user.username, telegram_id=user.telegram_id)


class SAUserGateway(SAGateway, UserGateway):
    async def check_exists(self, telegram_id: UUID) -> bool:
        exists = (
            await self.session.execute(
                select(select(UserModel).where(UserModel.telegram_id == telegram_id).exists())
            )
        ).one_or_none()
        return exists is not None and exists[0]

    async def get_by_telegram_id(self, telegram_id: str) -> User:
        model: UserModel = (
            await self.session.scalars(
                select(UserModel).where(UserModel.telegram_id == telegram_id).limit(1)
            )
        ).one_or_none()
        return convert_db_to_domain(model)

    async def create(self, user: User) -> None:
        model = convert_domain_to_db(user)

        try:
            self.session.add(model)
            await self.session.flush()
        except DBAPIError as e:
            self._parse_exc(e, user)

    @staticmethod
    def _parse_exc(err: DBAPIError, user: User) -> NoReturn:
        match err.__cause__.__cause__.constraint_name:  # type: ignore
            case _:
                raise GatewayException from err
