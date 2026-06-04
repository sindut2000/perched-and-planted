from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.plant import PlantCreate, PlantResponse, PlantUpdate
from app.services import plants as plant_service

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    payload: PlantCreate,
    db: AsyncSession = Depends(get_db),
) -> PlantResponse:
    plant = await plant_service.create_plant(db, payload)
    return PlantResponse.model_validate(plant)


@router.get("", response_model=list[PlantResponse])
async def list_plants(db: AsyncSession = Depends(get_db)) -> list[PlantResponse]:
    plants = await plant_service.list_plants(db)
    return [PlantResponse.model_validate(plant) for plant in plants]


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant_id: int,
    db: AsyncSession = Depends(get_db),
) -> PlantResponse:
    plant = await plant_service.get_plant(db, plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return PlantResponse.model_validate(plant)


@router.patch("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_id: int,
    payload: PlantUpdate,
    db: AsyncSession = Depends(get_db),
) -> PlantResponse:
    plant = await plant_service.update_plant(db, plant_id, payload)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return PlantResponse.model_validate(plant)


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await plant_service.delete_plant(db, plant_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
