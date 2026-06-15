from __future__ import annotations

import logging

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class SmsError(Exception):
    pass


class SmsNotConfiguredError(Exception):
    pass


def sms_is_configured(settings: Settings) -> bool:
    twilio = settings.twilio
    return bool(twilio.account_sid and twilio.auth_token and twilio.from_number)


async def send_sms(settings: Settings, to_number: str, body: str) -> None:
    if not sms_is_configured(settings):
        raise SmsNotConfiguredError("Twilio credentials are not configured")

    twilio = settings.twilio
    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio.account_sid}/Messages.json"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            url,
            data={"To": to_number, "From": twilio.from_number, "Body": body},
            auth=(twilio.account_sid, twilio.auth_token),
        )

    if response.status_code >= 400:
        logger.error("Twilio SMS failed: status=%s body=%s", response.status_code, response.text)
        raise SmsError(f"Twilio returned {response.status_code}")

    logger.info("SMS sent to %s", to_number[-4:].rjust(len(to_number), "*"))
