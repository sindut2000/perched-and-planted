import pytest
from app.models.plant import Plant
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def clean_plants(db_session: AsyncSession) -> None:
    await db_session.execute(delete(Plant))
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_plant(client: AsyncClient) -> None:
    response = await client.post(
        "/plants",
        json={"name": "Monstera", "species": "Monstera deliciosa", "location": "Balcony"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Monstera"
    assert payload["species"] == "Monstera deliciosa"
    assert payload["watering_interval_days"] == 7
    assert payload["id"] is not None


@pytest.mark.asyncio
async def test_create_plant_rejects_empty_name(client: AsyncClient) -> None:
    response = await client.post("/plants", json={"name": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_plants(client: AsyncClient) -> None:
    await client.post("/plants", json={"name": "Basil"})
    await client.post("/plants", json={"name": "Mint"})

    response = await client.get("/plants")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert {plant["name"] for plant in payload} == {"Basil", "Mint"}


@pytest.mark.asyncio
async def test_get_plant(client: AsyncClient) -> None:
    create_response = await client.post("/plants", json={"name": "Fern"})
    plant_id = create_response.json()["id"]

    response = await client.get(f"/plants/{plant_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Fern"


@pytest.mark.asyncio
async def test_get_plant_not_found(client: AsyncClient) -> None:
    response = await client.get("/plants/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_plant(client: AsyncClient) -> None:
    create_response = await client.post("/plants", json={"name": "Cactus"})
    plant_id = create_response.json()["id"]

    response = await client.patch(
        f"/plants/{plant_id}",
        json={"location": "Sunny window", "watering_interval_days": 14},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["location"] == "Sunny window"
    assert payload["watering_interval_days"] == 14


@pytest.mark.asyncio
async def test_delete_plant(client: AsyncClient) -> None:
    create_response = await client.post("/plants", json={"name": "Orchid"})
    plant_id = create_response.json()["id"]

    delete_response = await client.delete(f"/plants/{plant_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/plants/{plant_id}")
    assert get_response.status_code == 404
