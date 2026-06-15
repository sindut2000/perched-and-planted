import pytest
from app.models.plant import Plant
from httpx import AsyncClient
from sqlalchemy import delete, text
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
async def test_update_plant_rejects_explicit_null_on_required_field(
    client: AsyncClient,
) -> None:
    create_response = await client.post("/plants", json={"name": "Aloe"})
    plant_id = create_response.json()["id"]

    for body in ({"name": None}, {"watering_interval_days": None}):
        response = await client.patch(f"/plants/{plant_id}", json=body)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_db_defaults_and_updated_at_trigger(db_session: AsyncSession) -> None:
    # Raw insert omitting watering_interval_days relies on the DB server_default.
    await db_session.execute(
        text(
            "INSERT INTO plants (name, updated_at) "
            "VALUES ('Raw', '2000-01-01T00:00:00+00')"
        )
    )
    await db_session.commit()

    row = (
        await db_session.execute(
            text(
                "SELECT watering_interval_days, updated_at "
                "FROM plants WHERE name = 'Raw'"
            )
        )
    ).one()
    assert row.watering_interval_days == 7
    assert row.updated_at.year == 2000

    # A raw UPDATE that does not set updated_at must still bump it via the trigger.
    await db_session.execute(
        text("UPDATE plants SET location = 'shelf' WHERE name = 'Raw'")
    )
    await db_session.commit()

    bumped = (
        await db_session.execute(
            text("SELECT updated_at FROM plants WHERE name = 'Raw'")
        )
    ).scalar_one()
    assert bumped.year > 2000


@pytest.mark.asyncio
async def test_delete_plant(client: AsyncClient) -> None:
    create_response = await client.post("/plants", json={"name": "Orchid"})
    plant_id = create_response.json()["id"]

    delete_response = await client.delete(f"/plants/{plant_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/plants/{plant_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_update_plant_not_found(client: AsyncClient) -> None:
    response = await client.patch("/plants/99999", json={"location": "Shelf"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_plant_not_found(client: AsyncClient) -> None:
    response = await client.delete("/plants/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_water_plant_not_found(client: AsyncClient) -> None:
    response = await client.post("/plants/99999/water")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_plant_rejects_invalid_watering_interval(client: AsyncClient) -> None:
    response = await client.post("/plants", json={"name": "Cactus", "watering_interval_days": 0})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_plants_empty(client: AsyncClient) -> None:
    response = await client.get("/plants")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_plant_rejects_name_too_long(client: AsyncClient) -> None:
    response = await client.post("/plants", json={"name": "A" * 101})
    assert response.status_code == 422
