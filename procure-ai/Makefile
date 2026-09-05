.PHONY: up down build migrate seed test logs setup shell-db

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

migrate:
	docker-compose exec backend alembic upgrade head

seed:
	docker-compose exec backend python -m app.db.seed

logs:
	docker-compose logs -f

test:
	docker-compose exec backend pytest

setup: build up
	@echo "Waiting for DB to be ready..."
	@sleep 5
	make migrate
	make seed

shell-db:
	docker-compose exec db psql -U postgres -d procure_ai
