from dataclasses import dataclass

import anyio.from_thread
from aiogram import Bot, Dispatcher

from src.application.common.usecase import Usecase


@dataclass(slots=True)
class DispatchUpdateDTO:
    raw_update: dict


class DispatchUpdate(Usecase[DispatchUpdateDTO, None]):
    __slots__ = ("bot", "dp")

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp

    async def __call__(self, data: DispatchUpdateDTO) -> None:
        await self.dp.feed_raw_update(self.bot, data.raw_update)
