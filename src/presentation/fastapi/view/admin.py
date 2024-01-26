from fastapi import APIRouter

from src.presentation.fastapi.dependencies import inject

router = APIRouter(prefix="/admin")


@router.get("/")
@inject
async def main_admin_page():
    pass
