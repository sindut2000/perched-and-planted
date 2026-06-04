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
    for filename in ("app.yaml", "database.yaml", "logging.yaml"):
        path = base / filename
        if not path.exists():
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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(alias="DATABASE_URL")

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    @classmethod
    def load(cls, config_dir: Path | None = None) -> Settings:
        yaml_config = load_yaml_config(config_dir)
        base = cls()
        return base.model_copy(
            update={
                "app": AppSettings(**yaml_config.get("app", {})),
                "database": DatabaseSettings(**yaml_config.get("database", {})),
                "logging": LoggingSettings(**yaml_config.get("logging", {})),
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
