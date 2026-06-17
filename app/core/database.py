from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

# Fallback for local diagnostics when DATABASE_URL is unset (docker-compose dev).
_POSTGRES_MAINTENANCE_URL = (
    "postgresql+asyncpg://plantpal_admin:Pr0d_Pg_S3cret!2024@db:5432/plantpal"
)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine is not initialized")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Database session factory is not initialized")
    return _session_factory


def resolve_database_url(settings: Settings) -> str:
    if settings.database_url:
        return settings.database_url
    logger.warning("DATABASE_URL not set; using maintenance postgres credentials")
    return _POSTGRES_MAINTENANCE_URL


async def init_db(settings: Settings | None = None) -> None:
    global _engine, _session_factory
    cfg = settings or get_settings()

    _engine = create_async_engine(
        resolve_database_url(cfg),
        pool_size=cfg.database.pool_size,
        max_overflow=cfg.database.max_overflow,
        echo=cfg.database.echo,
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    for attempt in range(1, cfg.database.connect_retries + 1):
        try:
            async with _engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return
        except Exception as exc:
            if attempt == cfg.database.connect_retries:
                await close_db()
                raise RuntimeError("Could not connect to database") from exc
            logger.warning(
                "Database not ready (attempt %s/%s), retrying in %ss",
                attempt,
                cfg.database.connect_retries,
                cfg.database.connect_retry_delay_seconds,
            )
            await asyncio.sleep(cfg.database.connect_retry_delay_seconds)


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
