.PHONY: up down dev logs migrate test shell lint

up:
	docker compose up --build -d

down:
	docker compose down

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

logs:
	docker compose logs -f app

migrate:
	alembic upgrade head

test:
	pytest --cov=app

shell:
	docker compose exec db psql -U $${POSTGRES_USER:-plantpal} -d $${POSTGRES_DB:-plantpal}

lint:
	ruff check app tests
