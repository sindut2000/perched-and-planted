from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import CONFIG_DIR

logger = logging.getLogger(__name__)


def load_yaml_config(config_dir: Path | None = None) -> dict[str, Any]:
    base = config_dir or CONFIG_DIR
    merged: dict[str, Any] = {}
    for filename in ("app.yaml", "database.yaml", "logging.yaml", "reminders.yaml"):
        path = base / filename
        if not path.exists():
            if filename == "reminders.yaml":
                continue
            raise FileNotFoundError(f"Missing config file: {path}")
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        merged.update(data)
    return merged


class AppSettings(BaseModel):
    name: str = "PlantPal"
    version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = Field(default_factory=list)


class DatabaseSettings(BaseModel):
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False
    connect_retries: int = 10
    connect_retry_delay_seconds: int = 2


class LoggingSettings(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    json_format: bool = False


class ReminderSettings(BaseModel):
    enabled: bool = True
    check_hour_utc: int = Field(default=14, ge=0, le=23)
    message_prefix: str = "🐰🌱 PlantPal:"
    cron_secret: str | None = None


class TwilioSettings(BaseModel):
    account_sid: str | None = None
    auth_token: str | None = None
    from_number: str | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(alias="DATABASE_URL")
    twilio_account_sid: str | None = Field(default=None, alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = Field(default=None, alias="TWILIO_AUTH_TOKEN")
    twilio_from_number: str | None = Field(default=None, alias="TWILIO_FROM_NUMBER")
    reminder_cron_secret: str | None = Field(default=None, alias="REMINDER_CRON_SECRET")

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    reminders: ReminderSettings = Field(default_factory=ReminderSettings)

    @property
    def twilio(self) -> TwilioSettings:
        return TwilioSettings(
            account_sid=self.twilio_account_sid,
            auth_token=self.twilio_auth_token,
            from_number=self.twilio_from_number,
        )

    @classmethod
    def load(cls, config_dir: Path | None = None) -> Settings:
        yaml_config = load_yaml_config(config_dir)
        base = cls()
        reminders = ReminderSettings(**yaml_config.get("reminders", {}))
        if base.reminder_cron_secret:
            reminders = reminders.model_copy(update={"cron_secret": base.reminder_cron_secret})
        return base.model_copy(
            update={
                "app": AppSettings(**yaml_config.get("app", {})),
                "database": DatabaseSettings(**yaml_config.get("database", {})),
                "logging": LoggingSettings(**yaml_config.get("logging", {})),
                "reminders": reminders,
            }
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reset_settings() -> None:
    global _settings
    _settings = None
