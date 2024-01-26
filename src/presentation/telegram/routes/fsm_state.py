from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    thread_started = State()
