from datetime import datetime, timedelta, timezone

import pytest
from app.models.plant import Plant
from app.services.watering import (
    list_due_plants,
    mark_plant_watered,
    next_watering_at,
    watering_status,
)
from sqlalchemy.ext.asyncio import AsyncSession


def _plant(
    *,
    name: str = "Fern",
    interval: int = 7,
    last_watered_at: datetime | None = None,
    created_at: datetime | None = None,
) -> Plant:
    now = datetime.now(timezone.utc)
    return Plant(
        id=1,
        name=name,
        watering_interval_days=interval,
        last_watered_at=last_watered_at,
        created_at=created_at or now,
        updated_at=now,
    )


def test_watering_status_uses_created_at_when_never_watered() -> None:
    created = datetime(2026, 6, 1, tzinfo=timezone.utc)
    plant = _plant(created_at=created, interval=3)

    next_at, is_due, days_until = watering_status(plant)

    assert next_at == created + timedelta(days=3)
    assert is_due is (datetime.now(timezone.utc) >= next_at)
    assert days_until == (next_at.date() - datetime.now(timezone.utc).date()).days


def test_next_watering_at_uses_last_watered_at() -> None:
    watered = datetime(2026, 6, 10, tzinfo=timezone.utc)
    plant = _plant(last_watered_at=watered, interval=5)

    assert next_watering_at(plant) == watered + timedelta(days=5)


@pytest.mark.asyncio
async def test_list_due_plants(db_session: AsyncSession) -> None:
    overdue = Plant(
        name="Due Plant",
        watering_interval_days=1,
        last_watered_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    fresh = Plant(
        name="Fresh Plant",
        watering_interval_days=7,
        last_watered_at=datetime.now(timezone.utc),
    )
    db_session.add_all([overdue, fresh])
    await db_session.commit()

    due = await list_due_plants(db_session)

    assert [plant.name for plant in due] == ["Due Plant"]


@pytest.mark.asyncio
async def test_mark_plant_watered(db_session: AsyncSession) -> None:
    plant = Plant(name="Basil", watering_interval_days=3)
    db_session.add(plant)
    await db_session.commit()
    await db_session.refresh(plant)

    updated = await mark_plant_watered(db_session, plant.id)

    assert updated is not None
    assert updated.last_watered_at is not None
    assert updated.last_watered_at <= datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_mark_plant_watered_missing_returns_none(db_session: AsyncSession) -> None:
    assert await mark_plant_watered(db_session, 99999) is None


@pytest.mark.asyncio
async def test_list_due_plants_empty(db_session: AsyncSession) -> None:
    due = await list_due_plants(db_session)
    assert due == []


def test_watering_status_fresh_plant_not_due() -> None:
    now = datetime.now(timezone.utc)
    plant = _plant(last_watered_at=now, interval=7)

    _next_at, is_due, days_until = watering_status(plant)

    assert is_due is False
    assert days_until > 0
