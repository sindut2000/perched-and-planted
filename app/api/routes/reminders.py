from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.schemas.reminders import (
    ReminderSendResponse,
    ReminderSettingsResponse,
    ReminderSettingsUpdate,
)
from app.services import reminders as reminder_service
from app.services import settings_store
from app.services import sms as sms_service

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/settings", response_model=ReminderSettingsResponse)
async def get_reminder_settings(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ReminderSettingsResponse:
    phone = await settings_store.get_reminder_phone(db)
    return ReminderSettingsResponse(
        phone=phone,
        sms_configured=sms_service.sms_is_configured(settings),
        reminders_enabled=settings.reminders.enabled,
    )


@router.put("/settings", response_model=ReminderSettingsResponse)
async def update_reminder_settings(
    payload: ReminderSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ReminderSettingsResponse:
    phone = await settings_store.set_reminder_phone(db, payload.phone)
    return ReminderSettingsResponse(
        phone=phone,
        sms_configured=sms_service.sms_is_configured(settings),
        reminders_enabled=settings.reminders.enabled,
    )


@router.post("/send", response_model=ReminderSendResponse)
async def send_reminders(
    secret: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ReminderSendResponse:
    if settings.reminders.cron_secret:
        if secret != settings.reminders.cron_secret:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid secret")

    result = await reminder_service.send_due_plant_reminders(db, settings)
    return ReminderSendResponse(
        sent=bool(result.get("sent")),
        reason=result.get("reason"),  # type: ignore[arg-type]
        due_count=int(result.get("due_count", 0)),
        plants=list(result.get("plants", [])),
    )
