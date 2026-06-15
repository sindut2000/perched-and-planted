from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plant import Plant


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def watering_reference(plant: Plant) -> datetime:
    return plant.last_watered_at or plant.created_at


def next_watering_at(plant: Plant) -> datetime:
    return watering_reference(plant) + timedelta(days=plant.watering_interval_days)


def watering_status(plant: Plant) -> tuple[datetime, bool, int]:
    next_at = next_watering_at(plant)
    now = utc_now()
    days_until = (next_at.date() - now.date()).days
    is_due = now >= next_at
    return next_at, is_due, days_until


async def list_due_plants(session: AsyncSession) -> list[Plant]:
    plants = list((await session.execute(select(Plant).order_by(Plant.id))).scalars().all())
    return [plant for plant in plants if watering_status(plant)[1]]


async def mark_plant_watered(session: AsyncSession, plant_id: int, user_id: int) -> Plant | None:
    result = await session.execute(
        select(Plant).where(Plant.id == plant_id, Plant.user_id == user_id)
    )
    plant = result.scalar_one_or_none()
    if plant is None:
        return None

    plant.last_watered_at = utc_now()
    await session.commit()
    await session.refresh(plant)
    return plant
