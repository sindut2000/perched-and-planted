from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.plant import Plant
from app.services.watering import watering_status


class PlantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    species: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=100)
    watering_interval_days: int = Field(default=7, ge=1)
    notes: str | None = None


class PlantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    species: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=100)
    watering_interval_days: int | None = Field(default=None, ge=1)
    last_watered_at: datetime | None = None
    notes: str | None = None

    @field_validator("name", "watering_interval_days")
    @classmethod
    def _reject_explicit_null(cls, value: object) -> object:
        # These map to NOT NULL columns. They may be omitted, but an explicit
        # null must be rejected as a 422 rather than reaching the DB as a 500.
        if value is None:
            raise ValueError("may not be null")
        return value


class PlantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    species: str | None
    location: str | None
    watering_interval_days: int
    last_watered_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    next_watering_at: datetime
    is_due: bool
    days_until_watering: int

    @classmethod
    def from_plant(cls, plant: Plant) -> Self:
        next_at, is_due, days_until = watering_status(plant)
        return cls(
            id=plant.id,
            name=plant.name,
            species=plant.species,
            location=plant.location,
            watering_interval_days=plant.watering_interval_days,
            last_watered_at=plant.last_watered_at,
            notes=plant.notes,
            created_at=plant.created_at,
            updated_at=plant.updated_at,
            next_watering_at=next_at,
            is_due=is_due,
            days_until_watering=days_until,
        )
