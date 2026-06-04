from pathlib import Path

import pytest
from app.core.config import Settings, get_settings, load_yaml_config, reset_settings
from pydantic import ValidationError


def test_load_yaml_config_merges_files() -> None:
    config = load_yaml_config()
    assert config["app"]["name"] == "PlantPal"
    assert config["database"]["pool_size"] == 5
    assert config["logging"]["level"] == "INFO"
    assert config["logging"]["json_format"] is False


def test_settings_loads_from_yaml_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://plantpal:secret@localhost:5432/plantpal",
    )
    reset_settings()
    settings = Settings.load()
    assert settings.app.name == "PlantPal"
    assert settings.database.pool_size == 5
    assert "plantpal" in settings.database_url


def test_settings_requires_database_url(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.chdir(tmp_path)
    reset_settings()
    with pytest.raises(ValidationError):
        Settings()


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://plantpal:secret@localhost:5432/plantpal",
    )
    reset_settings()
    first = get_settings()
    second = get_settings()
    assert first is second
