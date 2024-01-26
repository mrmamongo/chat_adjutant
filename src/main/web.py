from dishka import AsyncContainer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from src.config import ApiConfig
from src.presentation.fastapi.setup import setup_routes


def container_middleware(container):
    async def add_request_container(request: Request, call_next):
        async with container({Request: request}) as sub:
            request.state.container = sub
            return await call_next(request)

    return add_request_container


async def setup_fastapi(container: AsyncContainer, config: ApiConfig, token: str) -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(container_middleware(container))

    setup_routes(app, token)
    # await setup_admin(app, container)
    return app
