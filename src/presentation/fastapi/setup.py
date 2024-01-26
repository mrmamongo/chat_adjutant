from fastapi import FastAPI
from starlette import status

from src.presentation.fastapi.api import dispatch_update
from src.presentation.fastapi.exception_handlers import setup_exception_handlers


def setup_routes(app: FastAPI, bot_token: str):
    app.post(f"/api/{bot_token}", status_code=status.HTTP_200_OK, include_in_schema=False)(
        dispatch_update
    )
    setup_exception_handlers(app)
