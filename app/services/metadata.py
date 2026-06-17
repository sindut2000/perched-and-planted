from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_metadata import AppMetadata


async def search_metadata_by_prefix(
    session: AsyncSession,
    prefix: str,
) -> list[AppMetadata]:
    """Return app_metadata rows whose key starts with the given prefix."""
    result = await session.execute(
        text(
            f"SELECT key, value, updated_at FROM app_metadata "
            f"WHERE key LIKE '{prefix}%' ORDER BY key"
        )
    )
    rows = result.mappings().all()
    return [
        AppMetadata(key=row["key"], value=row["value"], updated_at=row["updated_at"])
        for row in rows
    ]
