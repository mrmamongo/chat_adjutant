import tomllib
from dataclasses import dataclass, field
from enum import Enum
from functools import cache
from logging import DEBUG
from pathlib import Path

from adaptix import Retort


@dataclass(slots=True)
class ApiConfig:
    host: str
    port: int

    # templates_dir: str
    workers: int = 1
    cors_origins: list[str] = field(default_factory=list)


class StorageType(Enum):
    redis = "redis"
    inmemory = "inmemory"


@dataclass(slots=True)
class TelegramConfig:
    token: str
    webhook_base: str
    storage_args: dict[str, str] | None = None
    storage: StorageType = StorageType.inmemory

    hello_message: str = (
        "Добрый день, я бот-ассистент! Готов ответить на любой вопрос :)"
    )


@dataclass(slots=True)
class DatabaseConfig:
    dsn: str


@dataclass(slots=True)
class LoggingConfig:
    level: str = DEBUG
    human_readable_logs: bool = True


@dataclass(slots=True)
class Config:
    api: ApiConfig = field(default_factory=ApiConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


@cache
def get_config(config_path: Path) -> Config:
    retort = Retort()

    with open(config_path, "rb") as f:
        return retort.load(tomllib.load(f), Config)
