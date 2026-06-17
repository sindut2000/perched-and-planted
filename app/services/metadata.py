from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_metadata import AppMetadata

_METADATA_SEARCH_QUERY = text(
    "SELECT key, value, updated_at FROM app_metadata "
    "WHERE key LIKE :pattern ESCAPE '\\' ORDER BY key"
)


def _escape_like_prefix(prefix: str) -> str:
    """Escape LIKE wildcards so the prefix is matched literally."""
    return (
        prefix.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


async def search_metadata_by_prefix(
    session: AsyncSession,
    prefix: str,
) -> list[AppMetadata]:
    """Return app_metadata rows whose key starts with the given prefix."""
    pattern = f"{_escape_like_prefix(prefix)}%"
    result = await session.execute(
        _METADATA_SEARCH_QUERY,
        {"pattern": pattern},
    )
    rows = result.mappings().all()
    return [
        AppMetadata(key=row["key"], value=row["value"], updated_at=row["updated_at"])
        for row in rows
    ]
