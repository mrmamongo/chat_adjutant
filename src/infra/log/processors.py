from collections.abc import Callable
from typing import Any
from uuid import UUID

import orjson
import structlog

ProcessorType = Callable[
    [
        structlog.types.WrappedLogger,
        str,
        structlog.types.EventDict,
    ],
    str | bytes,
]


def additionally_serialize(obj: Any) -> Any:
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"TypeError: Type is not JSON serializable: {type(obj)}")


def serialize_to_json(data: Any, default: Any) -> str:
    return orjson.dumps(data, default=additionally_serialize).decode()


def get_json_processor(
    serializer: Callable[..., str | bytes] = serialize_to_json
) -> ProcessorType:
    return structlog.processors.JSONRenderer(serializer)


def get_console_processor(colors: bool = True) -> ProcessorType:
    return structlog.dev.ConsoleRenderer(colors=colors)
