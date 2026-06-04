from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.root import RootResponse

router = APIRouter(tags=["root"])


@router.get("/", response_model=RootResponse)
async def read_root() -> RootResponse:
    settings = get_settings()
    return RootResponse(
        app=settings.app.name,
        version=settings.app.version,
    )
