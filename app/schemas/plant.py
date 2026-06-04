from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
