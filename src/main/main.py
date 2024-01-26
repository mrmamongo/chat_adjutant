import asyncio
import os
from pathlib import Path

import structlog
import uvicorn
from dishka import make_async_container

from src.application.common.exceptions import ApplicationException
from src.config import Config, get_config
from src.infra.log.setup import setup_logging
from src.main.di import DIProvider
from src.main.interactor_provider import InteractorProvider
from src.main.web import setup_fastapi
from src.presentation.telegram.middlewares import ContainerMiddleware
from src.presentation.telegram.setup import setup_dispatcher

logger = structlog.get_logger(__name__)


async def run() -> None:
    config_path = Path(os.getenv("CONFIG_PATH"))
    if not config_path.exists():
        raise ApplicationException("Config file does not exist")

    config: Config = get_config(config_path)
    setup_logging(config.logging)

    bot, dispatcher = await setup_dispatcher(config.telegram)
    async with make_async_container(
        DIProvider(config, dispatcher, bot),
        InteractorProvider(),
        with_lock=True,
    ) as container:
        dispatcher.update.middleware(ContainerMiddleware(container))

        await logger.ainfo("Initializing fastapi")
        fastapi = await setup_fastapi(container, config.api, config.telegram.token)
        await logger.ainfo("Starting service")

        try:
            server = uvicorn.Server(
                config=uvicorn.Config(
                    app=fastapi,
                    host=config.api.host,
                    port=config.api.port,
                    workers=config.api.workers,
                )
            )
            await server.serve()
        finally:
            await container.close()


def main() -> None:
    try:
        asyncio.run(run())
        exit(os.EX_OK)
    except SystemExit:
        exit(os.EX_OK)
    except ApplicationException:
        exit(os.EX_SOFTWARE)
    except BaseException:
        logger.exception("Unexpected error occurred")
        exit(os.EX_SOFTWARE)


if __name__ == "__main__":
    main()
