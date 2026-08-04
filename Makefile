COMPOSE := docker compose
SCALE ?= small

.PHONY: up down seed test test-unit dev logs shell clean

up:
	$(COMPOSE) up -d --build
	@echo "neo4j browser: http://localhost:7474   api: http://localhost:8000/docs"

down:
	$(COMPOSE) down

seed:
	$(COMPOSE) run --rm app python scripts/seed.py --scale $(SCALE)

test:
	$(COMPOSE) run --rm app pytest -q

test-unit:
	$(COMPOSE) run --rm app pytest -q -m "not graph"

dev:
	$(COMPOSE) up -d neo4j
	$(COMPOSE) run --rm --service-ports app \
		uvicorn batchwatch.api:app --host 0.0.0.0 --port 8000 --reload

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) run --rm app bash

clean:
	$(COMPOSE) down -v
