from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.constants import STATIC_DIR

router = APIRouter(tags=["root"])


@router.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/api", include_in_schema=False)
async def api_info() -> dict[str, str]:
    return {"message": "PlantPal API — see /docs for endpoints"}
