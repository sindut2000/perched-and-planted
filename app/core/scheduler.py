from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import Settings
from app.core.database import get_session_factory
from app.services import reminders as reminder_service

logger = logging.getLogger(__name__)


def create_scheduler(settings: Settings) -> AsyncIOScheduler | None:
    if settings.app_env == "test" or not settings.reminders.enabled:
        return None

    scheduler = AsyncIOScheduler()

    async def run_daily_reminders() -> None:
        session_factory = get_session_factory()
        async with session_factory() as session:
            result = await reminder_service.send_due_plant_reminders(session, settings)
            logger.info("Daily reminder job finished: %s", result)

    scheduler.add_job(
        run_daily_reminders,
        CronTrigger(hour=settings.reminders.check_hour_utc, minute=0),
        id="daily_plant_reminders",
        replace_existing=True,
    )
    return scheduler
