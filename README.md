# PlantPal

Plant monitoring system — make your balcony greener.

Plant care tracker API — watering schedules, health notes, Telegram notifications, and (eventually) ESP32 soil sensors.

## Quick start

### Option A — Docker (full stack)

```bash
cp .env.example .env
make up
open http://localhost:8000/docs
```

### Option B — Desktop PostgreSQL + local Python

1. Install and start Postgres ([Homebrew](https://brew.sh) or [Postgres.app](https://postgresapp.com)):

```bash
createuser plantpal -P
createdb plantpal -O plantpal
```

2. Configure and run:

```bash
cp .env.example .env   # set DATABASE_URL with your real password
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
open http://localhost:8000/docs
```

## Endpoints

| URL | Description |
|-----|-------------|
| `/` | App name, version, links |
| `/health` | Live PostgreSQL connectivity check |
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |

## Configuration

- **Behavior** → YAML files in `config/`
- **Secrets** → `.env` (copy from `.env.example`, never commit)

Required env var: `DATABASE_URL`

## Development commands

```bash
make up        # Docker: start app + Postgres
make down      # Docker: stop containers
make dev       # Docker with hot reload
make migrate   # alembic upgrade head
make test      # pytest against real Postgres
make lint      # ruff check
make shell     # psql into Docker Postgres
```

## Project layout

```
app/api/           Route handlers (thin)
app/services/      Business logic
app/models/        SQLAlchemy models
app/schemas/       Pydantic schemas
app/core/          Config, database, logging
config/            YAML configuration
tests/             pytest (real PostgreSQL)
alembic/           Database migrations
```

## Cursor rules

Project conventions for AI-assisted development live in [`.cursor/rules/`](.cursor/rules/).

## CodeRabbit demo

This repo is used to showcase [CodeRabbit](https://coderabbit.ai) reviews. See `.coderabbit.yaml` and `.cursor/rules/coderabbit-demo.mdc`.
