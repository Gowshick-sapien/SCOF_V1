.PHONY: up down build generate etl test lint clean

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

generate:
	docker compose run --rm simulation python -m src.main

etl:
	docker compose run --rm etl python -m src.main

test:
	pytest

lint:
	ruff check .

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
