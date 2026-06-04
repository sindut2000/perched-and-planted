from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncGenerator

import pytest
from app.core.config import get_settings, reset_settings
from app.core.database import close_db, get_session_factory, init_db
from app.main import create_app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session", autouse=True)
def configure_test_env() -> None:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://plantpal:plantpal@localhost:5432/plantpal",
    )
    os.environ.setdefault("APP_ENV", "test")
    reset_settings()


@pytest.fixture(scope="session", autouse=True)
def run_migrations(configure_test_env: None) -> None:
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.fail(
            "Alembic migrations failed. Is PostgreSQL running?\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


@pytest.fixture
async def app():
    reset_settings()
    application = create_app()
    settings = get_settings()
    await init_db(settings)
    yield application
    await close_db()
    reset_settings()


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.fixture
async def db_session(app) -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
