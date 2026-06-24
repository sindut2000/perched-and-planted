from unittest.mock import patch

import pytest
from app.core.config import get_settings
from app.models.app_metadata import AppMetadata
from app.services.reminders import build_reminder_message
from app.services.settings_store import REMINDER_PHONE_KEY
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def clean_reminder_settings(db_session: AsyncSession) -> None:
    await db_session.execute(
        delete(AppMetadata).where(AppMetadata.key == REMINDER_PHONE_KEY)
    )
    await db_session.commit()


def test_build_reminder_message_single_plant() -> None:
    message = build_reminder_message(["Monstera"], "🐰🌱 PlantPal:")
    assert "Monstera" in message
    assert message.startswith("🐰🌱 PlantPal:")


def test_build_reminder_message_multiple_plants() -> None:
    message = build_reminder_message(["Basil", "Mint", "Fern"], "🐰🌱 PlantPal:")
    assert "Basil, Mint, and Fern" in message


@pytest.mark.asyncio
async def test_get_reminder_settings(client: AsyncClient) -> None:
    response = await client.get("/reminders/settings")
    assert response.status_code == 200
    payload = response.json()
    assert payload["phone"] is None
    assert payload["sms_configured"] is False
    assert payload["reminders_enabled"] is True


@pytest.mark.asyncio
async def test_update_reminder_settings(client: AsyncClient, db_session: AsyncSession) -> None:
    response = await client.put(
        "/reminders/settings",
        json={"phone": "+15551234567"},
    )
    assert response.status_code == 200
    assert response.json()["phone"] == "+15551234567"


@pytest.mark.asyncio
async def test_update_reminder_settings_rejects_invalid_phone(client: AsyncClient) -> None:
    response = await client.put("/reminders/settings", json={"phone": "5551234567"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_reminders_without_phone(client: AsyncClient) -> None:
    response = await client.post("/reminders/send")
    assert response.status_code == 200
    payload = response.json()
    assert payload["sent"] is False
    assert payload["reason"] == "no_phone"


@pytest.mark.asyncio
async def test_water_plant_endpoint(client: AsyncClient) -> None:
    create_response = await client.post("/plants", json={"name": "Pothos"})
    plant_id = create_response.json()["id"]

    response = await client.post(f"/plants/{plant_id}/water")
    assert response.status_code == 200
    payload = response.json()
    assert payload["last_watered_at"] is not None
    assert payload["is_due"] is False
    assert "next_watering_at" in payload


@pytest.mark.asyncio
async def test_plant_response_includes_watering_fields(client: AsyncClient) -> None:
    response = await client.post(
        "/plants",
        json={"name": "Snake Plant", "watering_interval_days": 10},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["watering_interval_days"] == 10
    assert "next_watering_at" in payload
    assert "days_until_watering" in payload
    assert "is_due" in payload


def test_build_reminder_message_two_plants() -> None:
    # Two-plant list produces Oxford comma: "A, and B" not "A and B".
    message = build_reminder_message(["Basil", "Mint"], "prefix:")
    assert "Basil, and Mint" in message


@pytest.mark.asyncio
async def test_send_reminders_with_wrong_cron_secret_returns_401(
    app: FastAPI,
) -> None:
    base_settings = get_settings()
    patched = base_settings.model_copy(
        update={"reminders": base_settings.reminders.model_copy(update={"cron_secret": "secret123"})}
    )
    app.dependency_overrides[get_settings] = lambda: patched
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            response = await http_client.post("/reminders/send?secret=wrong")
        assert response.status_code == 401
    finally:
        app.dependency_overrides.pop(get_settings, None)


@pytest.mark.asyncio
async def test_send_reminders_sms_not_configured(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    # Set a phone but leave Twilio env vars absent (test env default).
    await client.put("/reminders/settings", json={"phone": "+15551234567"})

    response = await client.post("/reminders/send")
    assert response.status_code == 200
    payload = response.json()
    assert payload["sent"] is False
    assert payload["reason"] == "sms_not_configured"


@pytest.mark.asyncio
async def test_send_reminders_none_due(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    # Set a phone; mock sms_is_configured so we reach the "none_due" branch.
    await client.put("/reminders/settings", json={"phone": "+15551234567"})

    with patch("app.services.reminders.sms.sms_is_configured", return_value=True):
        response = await client.post("/reminders/send")

    assert response.status_code == 200
    payload = response.json()
    assert payload["sent"] is False
    assert payload["reason"] == "none_due"
    assert payload["due_count"] == 0


@pytest.mark.asyncio
async def test_set_reminder_phone_upsert(client: AsyncClient) -> None:
    # First write.
    r1 = await client.put("/reminders/settings", json={"phone": "+15551234567"})
    assert r1.status_code == 200
    assert r1.json()["phone"] == "+15551234567"

    # Second write updates in place.
    r2 = await client.put("/reminders/settings", json={"phone": "+15559876543"})
    assert r2.status_code == 200
    assert r2.json()["phone"] == "+15559876543"

    # GET reflects the latest value.
    r3 = await client.get("/reminders/settings")
    assert r3.json()["phone"] == "+15559876543"
