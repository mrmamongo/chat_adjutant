import logging.config

import structlog
from sqlalchemy import log as sa_log
from structlog.processors import CallsiteParameter, CallsiteParameterAdder
from structlog.typing import EventDict

from src.config import LoggingConfig

from .processors import get_console_processor, get_json_processor


# https://github.com/hynek/structlog/issues/35#issuecomment-591321744
def rename_event_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Log entries keep the text message in the `event` field, but Datadog
    uses the `message` field. This processor moves the value from one field to
    the other.
    See https://github.com/hynek/structlog/issues/35#issuecomment-591321744
    """
    event_dict["message"] = event_dict.pop("event")
    return event_dict


def setup_logging(config: LoggingConfig) -> None:
    # Mute SQLAlchemy default logger handler
    sa_log._add_default_handler = lambda _: None  # type: ignore

    common_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=True),
        structlog.contextvars.merge_contextvars,
        structlog.processors.dict_tracebacks,
        CallsiteParameterAdder(
            (
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            )
        ),
    ]
    structlog_processors = [
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.UnicodeDecoder(),  # convert bytes to str
        # structlog.stdlib.render_to_log_kwargs,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        # structlog.processors.py.format_exc_info,  # print exceptions from event dict
    ]
    if not config.human_readable_logs:
        # We rename the `event` key to `message` only in JSON logs, as Datadog looks for the
        # `message` key but the pretty ConsoleRenderer looks for `event`
        common_processors.append(rename_event_key)
        # Format the exception only for JSON logs, as we want to pretty-print them when
        # using the ConsoleRenderer
        common_processors.append(structlog.processors.format_exc_info)
    logging_processors = (structlog.stdlib.ProcessorFormatter.remove_processors_meta,)
    logging_console_processors = (
        *logging_processors,
        get_console_processor() if config.human_readable_logs else get_json_processor(),
    )

    handler = logging.StreamHandler()
    handler.set_name("default")
    handler.setLevel(config.level)
    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=common_processors,  # type: ignore
        processors=logging_console_processors,
    )
    handler.setFormatter(console_formatter)

    handlers: list[logging.Handler] = [handler]

    logging.basicConfig(handlers=handlers, level=config.level)
    structlog.configure(
        processors=common_processors + structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        # wrapper_class=structlog.stdlib.AsyncBoundLoggerd,  # type: ignore  # noqa
        wrapper_class=structlog.stdlib.BoundLogger,  # type: ignore  # noqa
        cache_logger_on_first_use=True,
    )
