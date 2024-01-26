from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ContainerMiddleware(BaseMiddleware):
    def __init__(self, container):
        self.container = container

    async def __call__(
        self,
        handler,
        event,
        data,
    ):
        async with self.container({TelegramObject: event}) as subcontainer:
            data["container"] = subcontainer
            return await handler(event, data)
