from abc import ABC, abstractmethod


class AIAdapter(ABC):
    @abstractmethod
    async def initialize_thread(self):
        pass

    @abstractmethod
    async def request_message(self):
        pass
