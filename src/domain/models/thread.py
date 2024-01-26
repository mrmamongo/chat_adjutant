from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class Thread:
    user_id: UUID
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class RequestMessage:
    thread_id: UUID
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class ResponseMessage:
    message_id: UUID
    text: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class Message:
    id: UUID
    text: str
    timestamp: datetime
