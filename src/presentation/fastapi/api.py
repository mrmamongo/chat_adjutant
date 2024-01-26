from typing import Annotated

from dishka import Depends

from src.application.bot.dispatch_update import DispatchUpdate, DispatchUpdateDTO
from src.presentation.fastapi.dependencies import inject


@inject
async def dispatch_update(
    update: dict,
    dispatch_update_usecase: Annotated[DispatchUpdate, Depends()],
):
    await dispatch_update_usecase(DispatchUpdateDTO(raw_update=update))
