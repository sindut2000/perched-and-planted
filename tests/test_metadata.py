import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metadata_search_returns_schema_version(client: AsyncClient) -> None:
    response = await client.get("/metadata/search", params={"prefix": "schema"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["prefix"] == "schema"
    assert len(payload["results"]) == 1
    assert payload["results"][0]["key"] == "schema_version"
    assert payload["results"][0]["value"] == "1"
