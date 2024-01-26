from datetime import datetime

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseModel(DeclarativeBase):
    pass


class UserModel(BaseModel):
    __tablename__ = "users"

    id = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column()
    telegram_id: Mapped[str] = mapped_column(unique=True)


class ThreadModel(BaseModel):
    __tablename__ = "threads"

    id = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))


class RequestMessageModel(BaseModel):
    __tablename__ = "requests"

    id = mapped_column(UUID(as_uuid=True), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column()
    text: Mapped[str] = mapped_column()
    thread_id: Mapped[UUID] = mapped_column(ForeignKey("threads.id"))


class ResponseMessageModel(BaseModel):
    __tablename__ = "responses"

    id = mapped_column(ForeignKey("requests.id"), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column()
    text: Mapped[str] = mapped_column()
