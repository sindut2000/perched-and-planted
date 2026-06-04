from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.health import HealthResponse
from app.services.health import check_database

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def read_health(db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    try:
        db_health = await check_database(db)
    except Exception:
        body = HealthResponse(
            status="error",
            app=settings.app.name,
            version=settings.app.version,
            database="unavailable",
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=body.model_dump(),
        )

    return HealthResponse(
        status="ok",
        app=settings.app.name,
        version=settings.app.version,
        database="connected",
        schema_version=db_health.schema_version,
    )
