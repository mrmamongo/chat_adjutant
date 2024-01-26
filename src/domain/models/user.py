from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(slots=True)
class User:
    username: str
    telegram_id: str
    id: UUID = field(default_factory=uuid4)
