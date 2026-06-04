from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plant import Plant
from app.schemas.plant import PlantCreate, PlantUpdate


async def create_plant(session: AsyncSession, data: PlantCreate) -> Plant:
    plant = Plant(
        name=data.name,
        species=data.species,
        location=data.location,
        watering_interval_days=data.watering_interval_days,
        notes=data.notes,
    )
    session.add(plant)
    await session.commit()
    await session.refresh(plant)
    return plant


async def list_plants(session: AsyncSession) -> list[Plant]:
    result = await session.execute(select(Plant).order_by(Plant.id))
    return list(result.scalars().all())


async def get_plant(session: AsyncSession, plant_id: int) -> Plant | None:
    result = await session.execute(select(Plant).where(Plant.id == plant_id))
    return result.scalar_one_or_none()


async def update_plant(
    session: AsyncSession, plant_id: int, data: PlantUpdate
) -> Plant | None:
    plant = await get_plant(session, plant_id)
    if plant is None:
        return None

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(plant, field, value)

    await session.commit()
    await session.refresh(plant)
    return plant


async def delete_plant(session: AsyncSession, plant_id: int) -> bool:
    plant = await get_plant(session, plant_id)
    if plant is None:
        return False

    await session.delete(plant)
    await session.commit()
    return True
