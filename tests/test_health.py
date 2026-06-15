import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_connected(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app"] == "PlantPal"
    assert payload["database"] == "connected"
    assert payload["schema_version"] == "1"


@pytest.mark.asyncio
async def test_root_serves_frontend(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert "PlantPal" in response.text
    assert "🐰🌱" in response.text


@pytest.mark.asyncio
async def test_api_returns_app_info(client: AsyncClient) -> None:
    response = await client.get("/api")
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "PlantPal API — see /docs for endpoints"
