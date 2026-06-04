from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SCHEMA_VERSION_KEY
from app.models.app_metadata import AppMetadata


@dataclass
class DatabaseHealth:
    connected: bool
    schema_version: str | None = None


async def check_database(session: AsyncSession) -> DatabaseHealth:
    await session.execute(text("SELECT 1"))
    result = await session.execute(
        select(AppMetadata.value).where(AppMetadata.key == SCHEMA_VERSION_KEY)
    )
    schema_version = result.scalar_one_or_none()
    return DatabaseHealth(connected=True, schema_version=schema_version)
