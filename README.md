# SaaS Project Management Platform

A production-ready, multi-tenant SaaS project management platform built with **FastAPI**, **React**, and **PostgreSQL** — comparable in scope to Jira, Asana, and Linear.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Tailwind CSS, Zustand, React Query, Vite |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async) |
| Workers | Celery 5, Redis 7 (broker + cache + pub/sub) |
| Database | PostgreSQL 16 + read replica, S3-compatible object storage |
| Infra | Docker, Kubernetes + Helm, GitHub Actions, Terraform |
| AI | Anthropic Claude API (server-side proxy only) |
| Observability | Prometheus, Grafana, Sentry, OpenTelemetry, Loki |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/your-org/saas-platform.git
cd saas-platform

# Start local development environment
make dev

# Run database migrations
make migrate

# Run all tests
make test
```

The app will be available at:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/api/docs
- Redoc: http://localhost:8000/api/redoc
- MinIO console: http://localhost:9001
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- Mailhog: http://localhost:8025

## Project Structure

```
saas-platform/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # React 18 frontend
├── infra/
│   ├── terraform/    # Cloud infrastructure (AWS/Azure/DigitalOcean)
│   ├── k8s/          # Kubernetes manifests
│   └── helm/         # Helm chart
├── packages/
│   └── shared-types/ # Shared TypeScript types
└── .github/
    └── workflows/    # GitHub Actions CI/CD
```

## Architecture

The backend follows clean architecture with four strict layers:

```
Router → Service → Repository → Database
```

- **No SQL in routers.** No business logic in repositories.
- **All side effects** (emails, webhooks, AI calls) dispatched as Celery tasks — never synchronous in the request path.
- **Multi-tenancy** enforced via PostgreSQL Row-Level Security on every tenant-scoped table.

## Development

### Prerequisites

- Docker & Docker Compose
- Make
- Node.js 20+ (for frontend)
- Python 3.12+ (for local API development without Docker)

### Environment Variables

Copy the example env file and fill in your values:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

### Makefile Commands

```bash
make dev          # Start all services with docker-compose
make test         # Run all tests (unit + integration)
make test-unit    # Unit tests only
make test-e2e     # Playwright E2E tests
make migrate      # Run Alembic migrations
make lint         # Run linters (ruff, mypy, eslint)
make build        # Build production Docker images
make down         # Stop all services
make logs         # Tail logs for all services
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **Redoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Deployment

See [infra/README.md](infra/README.md) for full deployment documentation.

```bash
# Deploy to staging
make deploy-staging

# Deploy to production (requires release tag)
git tag v1.0.0 && git push origin v1.0.0
```

## Testing

```bash
# Unit tests with coverage
make test-unit

# Integration tests (spins up testcontainers)
make test-integration

# E2E tests against staging
make test-e2e

# Load tests with Locust
make test-load
```

## Security

- JWT RS256 authentication with rotating refresh tokens
- PostgreSQL Row-Level Security for tenant isolation
- RBAC: Admin, Manager, Member, Viewer roles
- OWASP Top-10 mitigations enforced
- Secrets managed via HashiCorp Vault / AWS Secrets Manager
- OWASP ZAP DAST runs in CI before every production deploy

## License

MIT
