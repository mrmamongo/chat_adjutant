from typing import Annotated

import structlog
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka import Depends

from src.application.thread.request_message import RequestMessage, RequestMessageInDTO
from src.application.user.init_user import InitUser, InitUserInDTO
from src.presentation.telegram.dependencies import inject
from src.presentation.telegram.routes.fsm_state import BotState

logger = structlog.get_logger(__name__)
router = Router()


@router.message(CommandStart())
@inject
async def init_user(
    message: Message,
    state: FSMContext,
    init_user_usecase: Annotated[InitUser, Depends()],
) -> None:
    await state.clear()
    initialized = await init_user_usecase(
        InitUserInDTO(
            user_id=str(message.from_user.id), username=message.from_user.username
        )
    )
    await state.set_state(BotState.thread_started)
    await state.update_data(thread_id=str(initialized.thread_id))

    await message.answer(initialized.hello_message)


@router.message(BotState.thread_started)
@inject
async def request_bot(
    message: Message,
    state: FSMContext,
    request_message_usecase: Annotated[RequestMessage, Depends()],
) -> None:
    thread_id = (await state.get_data()).get("thread_id")
    if thread_id is None:
        await message.answer("Пожалуйста, сначала инициализируйте бота командой /start")
        return
    response = await request_message_usecase(RequestMessageInDTO(thread_id=thread_id, text=message.text))
    await message.answer(response.answer)
