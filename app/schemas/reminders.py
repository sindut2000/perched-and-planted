from pydantic import BaseModel, Field


class ReminderSettingsResponse(BaseModel):
    phone: str | None
    sms_configured: bool
    reminders_enabled: bool


class ReminderSettingsUpdate(BaseModel):
    phone: str = Field(min_length=10, max_length=20, pattern=r"^\+[1-9]\d{1,14}$")


class ReminderSendResponse(BaseModel):
    sent: bool
    reason: str | None = None
    due_count: int = 0
    plants: list[str] = Field(default_factory=list)
