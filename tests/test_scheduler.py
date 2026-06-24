import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import ReminderSettings, Settings
from app.core.scheduler import create_scheduler


def _settings(app_env: str = "test", reminders_enabled: bool = True) -> Settings:
    base = Settings(DATABASE_URL="postgresql+asyncpg://x:x@localhost/x")
    return base.model_copy(
        update={
            "app_env": app_env,
            "reminders": ReminderSettings(enabled=reminders_enabled),
        }
    )


def test_create_scheduler_returns_none_in_test_env() -> None:
    settings = _settings(app_env="test", reminders_enabled=True)
    assert create_scheduler(settings) is None


def test_create_scheduler_returns_none_when_reminders_disabled() -> None:
    settings = _settings(app_env="production", reminders_enabled=False)
    assert create_scheduler(settings) is None


def test_create_scheduler_returns_scheduler_when_enabled() -> None:
    settings = _settings(app_env="production", reminders_enabled=True)
    scheduler = create_scheduler(settings)
    assert isinstance(scheduler, AsyncIOScheduler)
    job_ids = [job.id for job in scheduler.get_jobs()]
    assert "daily_plant_reminders" in job_ids