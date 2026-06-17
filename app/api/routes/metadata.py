from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.metadata import MetadataEntry, MetadataSearchResponse
from app.services.metadata import search_metadata_by_prefix

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/search", response_model=MetadataSearchResponse)
async def search_metadata(
    prefix: str = Query(..., min_length=1, max_length=64),
    db: AsyncSession = Depends(get_db),
):
    rows = await search_metadata_by_prefix(db, prefix)
    return MetadataSearchResponse(
        prefix=prefix,
        results=[
            MetadataEntry(
                key=row.key,
                value=row.value,
                updated_at=row.updated_at,
            )
            for row in rows
        ],
    )
