from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.services import settings_store, sms
from app.services.watering import list_due_plants

logger = logging.getLogger(__name__)


def build_reminder_message(plant_names: list[str], prefix: str) -> str:
    if len(plant_names) == 1:
        plants_line = plant_names[0]
    else:
        plants_line = ", ".join(plant_names[:-1]) + f", and {plant_names[-1]}"

    return f"{prefix} Time to water {plants_line}! 💧🌿"


async def send_due_plant_reminders(session: AsyncSession, settings: Settings) -> dict[str, object]:
    phone = await settings_store.get_reminder_phone(session)
    if not phone:
        return {"sent": False, "reason": "no_phone", "due_count": 0}

    if not sms.sms_is_configured(settings):
        return {"sent": False, "reason": "sms_not_configured", "due_count": 0}

    due_plants = await list_due_plants(session)
    if not due_plants:
        return {"sent": False, "reason": "none_due", "due_count": 0}

    message = build_reminder_message(
        [plant.name for plant in due_plants],
        settings.reminders.message_prefix,
    )
    await sms.send_sms(settings, phone, message)
    return {
        "sent": True,
        "due_count": len(due_plants),
        "plants": [plant.name for plant in due_plants],
    }
