from uuid import UUID

from src.domain.models.thread import RequestMessage, ResponseMessage, Thread


class ThreadService:
    def create_thread(self, user_id: UUID) -> Thread:
        return Thread(user_id=user_id)

    def create_request(self, thread_id: UUID, text: str) -> RequestMessage:
        return RequestMessage(thread_id=thread_id, text=text)

    def create_response(self, message_id: UUID, text: str) -> ResponseMessage:
        return ResponseMessage(message_id=message_id, text=text)
