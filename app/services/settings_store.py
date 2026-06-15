from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_metadata import AppMetadata

REMINDER_PHONE_KEY = "reminder_phone"


async def get_reminder_phone(session: AsyncSession) -> str | None:
    result = await session.execute(
        select(AppMetadata).where(AppMetadata.key == REMINDER_PHONE_KEY)
    )
    row = result.scalar_one_or_none()
    return row.value if row else None


async def set_reminder_phone(session: AsyncSession, phone: str) -> str:
    result = await session.execute(
        select(AppMetadata).where(AppMetadata.key == REMINDER_PHONE_KEY)
    )
    row = result.scalar_one_or_none()
    if row is None:
        row = AppMetadata(key=REMINDER_PHONE_KEY, value=phone)
        session.add(row)
    else:
        row.value = phone

    await session.commit()
    await session.refresh(row)
    return row.value
