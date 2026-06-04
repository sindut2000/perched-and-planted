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
async def test_root_returns_app_info(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["app"] == "PlantPal"
    assert payload["version"] == "0.1.0"
    assert payload["docs_url"] == "/docs"
    assert payload["health_url"] == "/health"
