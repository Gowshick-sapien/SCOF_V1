.PHONY: up down build generate etl test verify-d1 lint clean

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

verify-d1:
	python scripts/verify_d1.py

verify-d2:
	python scripts/verify_d2.py

verify-d3:
	python scripts/verify_d3.py

test:
	pytest

lint:
	ruff check .

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
