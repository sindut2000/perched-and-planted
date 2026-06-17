import pytest
from app.core.config import Settings
from app.core.database import resolve_database_url
from app.models.app_metadata import AppMetadata
from app.services.metadata import search_metadata_by_prefix
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession


def test_resolve_database_url_raises_when_database_url_unset() -> None:
    settings = Settings.model_construct(database_url="")
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        resolve_database_url(settings)


@pytest.mark.asyncio
@pytest.mark.parametrize("prefix", ["", "a" * 65])
async def test_metadata_search_rejects_invalid_prefix(
    client: AsyncClient,
    prefix: str,
) -> None:
    response = await client.get("/metadata/search", params={"prefix": prefix})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_metadata_search_returns_schema_version(client: AsyncClient) -> None:
    response = await client.get("/metadata/search", params={"prefix": "schema"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["prefix"] == "schema"
    assert len(payload["results"]) == 1
    assert payload["results"][0]["key"] == "schema_version"
    assert payload["results"][0]["value"] == "1"


@pytest.mark.asyncio
async def test_metadata_search_treats_percent_as_literal(
    db_session: AsyncSession,
) -> None:
    keys = ["likepct%match", "likepctXmatch"]
    for key in keys:
        db_session.add(AppMetadata(key=key, value="test"))
    await db_session.commit()

    try:
        rows = await search_metadata_by_prefix(db_session, "likepct%")
        assert [row.key for row in rows] == ["likepct%match"]
    finally:
        await db_session.execute(delete(AppMetadata).where(AppMetadata.key.in_(keys)))
        await db_session.commit()


@pytest.mark.asyncio
async def test_metadata_search_treats_underscore_as_literal(
    db_session: AsyncSession,
) -> None:
    keys = ["likeund_match", "likeundXmatch"]
    for key in keys:
        db_session.add(AppMetadata(key=key, value="test"))
    await db_session.commit()

    try:
        rows = await search_metadata_by_prefix(db_session, "likeund_")
        assert [row.key for row in rows] == ["likeund_match"]
    finally:
        await db_session.execute(delete(AppMetadata).where(AppMetadata.key.in_(keys)))
        await db_session.commit()


@pytest.mark.asyncio
async def test_metadata_search_uses_parameterized_query(
    db_session: AsyncSession,
) -> None:
    injection_prefix = "schema' OR '1'='1"
    rows = await search_metadata_by_prefix(db_session, injection_prefix)
    assert rows == []
