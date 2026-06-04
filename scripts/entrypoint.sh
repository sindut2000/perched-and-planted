#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for database..."
python - <<'PY'
import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

url = os.environ["DATABASE_URL"]
retries = int(os.environ.get("DB_CONNECT_RETRIES", "30"))
delay = float(os.environ.get("DB_CONNECT_RETRY_DELAY", "2"))


async def wait() -> None:
    engine = create_async_engine(url)
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            print("Database is ready")
            return
        except Exception as exc:
            print(f"Attempt {attempt}/{retries}: {exc}", file=sys.stderr)
            await asyncio.sleep(delay)
    await engine.dispose()
    sys.exit(1)


asyncio.run(wait())
PY

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
