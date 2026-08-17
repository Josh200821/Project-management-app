.PHONY: dev down logs migrate test test-unit test-integration test-e2e test-load lint build deploy-staging

# ── Local development ────────────────────────────────────────────────
dev:
	docker compose up --build -d
	@echo "✅  Services started. API: http://localhost:8000 | App: http://localhost:3000"

down:
	docker compose down -v

logs:
	docker compose logs -f

# ── Database ─────────────────────────────────────────────────────────
migrate:
	docker compose exec api alembic upgrade head

migrate-down:
	docker compose exec api alembic downgrade -1

migrate-create:
	@read -p "Migration name: " name; \
	docker compose exec api alembic revision --autogenerate -m "$$name"

seed:
	docker compose exec api python -m app.db.seed

# ── Testing ──────────────────────────────────────────────────────────
test: test-unit test-integration

test-unit:
	docker compose -f docker-compose.test.yml run --rm api \
		pytest apps/api/app/tests/unit -v --cov=app --cov-report=term-missing --cov-fail-under=80

test-integration:
	docker compose -f docker-compose.test.yml run --rm api \
		pytest apps/api/app/tests/integration -v

test-e2e:
	cd apps/web && npx playwright test

test-load:
	locust -f apps/api/tests/load/locustfile.py --host=http://localhost:8000

# ── Linting ──────────────────────────────────────────────────────────
lint:
	docker compose exec api ruff check app/
	docker compose exec api mypy app/
	cd apps/web && npm run lint

format:
	docker compose exec api ruff format app/
	cd apps/web && npm run format

# ── Build ────────────────────────────────────────────────────────────
build:
	docker compose build

build-prod:
	docker build -f apps/api/Dockerfile --target production -t saas-api:latest apps/api
	docker build -f apps/web/Dockerfile --target production -t saas-web:latest apps/web

# ── Deployment ───────────────────────────────────────────────────────
deploy-staging:
	gh workflow run cd-staging.yml

# ── Utilities ────────────────────────────────────────────────────────
shell-api:
	docker compose exec api bash

shell-db:
	docker compose exec db psql -U postgres -d saas_platform

redis-cli:
	docker compose exec redis redis-cli
