from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.core.config import Settings
from app.services.sms import SmsError, SmsNotConfiguredError, send_sms, sms_is_configured


def _settings_with_twilio(
    account_sid: str | None = "AC123",
    auth_token: str | None = "token456",
    from_number: str | None = "+15550000000",
) -> Settings:
    base = Settings(DATABASE_URL="postgresql+asyncpg://x:x@localhost/x")
    return base.model_copy(
        update={
            "twilio_account_sid": account_sid,
            "twilio_auth_token": auth_token,
            "twilio_from_number": from_number,
        }
    )


def test_sms_is_configured_false_when_no_credentials() -> None:
    settings = _settings_with_twilio(account_sid=None, auth_token=None, from_number=None)
    assert sms_is_configured(settings) is False


def test_sms_is_configured_false_when_partial_credentials() -> None:
    settings = _settings_with_twilio(account_sid="AC123", auth_token=None, from_number="+1555")
    assert sms_is_configured(settings) is False


def test_sms_is_configured_true_when_all_credentials_present() -> None:
    settings = _settings_with_twilio()
    assert sms_is_configured(settings) is True


@pytest.mark.asyncio
async def test_send_sms_raises_when_not_configured() -> None:
    settings = _settings_with_twilio(account_sid=None, auth_token=None, from_number=None)
    with pytest.raises(SmsNotConfiguredError):
        await send_sms(settings, "+15551234567", "Hello")


@pytest.mark.asyncio
async def test_send_sms_raises_sms_error_on_http_error() -> None:
    settings = _settings_with_twilio()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("app.services.sms.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(SmsError, match="400"):
            await send_sms(settings, "+15551234567", "Hello")


@pytest.mark.asyncio
async def test_send_sms_succeeds_on_2xx() -> None:
    settings = _settings_with_twilio()
    mock_response = MagicMock()
    mock_response.status_code = 201

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("app.services.sms.httpx.AsyncClient", return_value=mock_client):
        # Should not raise.
        await send_sms(settings, "+15551234567", "Hello")

    mock_client.post.assert_awaited_once()