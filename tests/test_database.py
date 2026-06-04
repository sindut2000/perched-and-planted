import pytest
from app.core.constants import SCHEMA_VERSION_KEY
from app.models.app_metadata import AppMetadata
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_app_metadata_schema_version_exists(db_session: AsyncSession) -> None:
    result = await db_session.execute(
        select(AppMetadata).where(AppMetadata.key == SCHEMA_VERSION_KEY)
    )
    row = result.scalar_one()
    assert row.value == "1"


@pytest.mark.asyncio
async def test_app_metadata_round_trip(db_session: AsyncSession) -> None:
    result = await db_session.execute(select(AppMetadata))
    rows = result.scalars().all()
    assert len(rows) >= 1
    assert all(row.key for row in rows)
