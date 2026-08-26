# SaaS Project Management Platform (Prototype)

An early-stage, **not-yet-functional** scaffold for a multi-tenant project management platform (Jira/Asana/Linear-style), built with FastAPI, React, and PostgreSQL.

> **Status: 🔴 Pre-alpha scaffold.** The repository lays out the intended architecture, dependencies, and folder structure, but the backend does not currently start, the test suite does not currently run, and CI is red across every job. This README documents the real current state and the work needed to get it running — see [CI Status & Known Issues](#ci-status--known-issues) and the [To-Do list](#to-do-list) below.

## Tech Stack

Dependencies below are declared in `pyproject.toml` / `package.json`, but not everything that depends on them is wired up yet (see Known Issues).

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS, Zustand, React Query, Vite |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async) |
| Workers | Celery 5, Redis 7 (broker + cache + pub/sub) |
| Database | PostgreSQL 16, S3-compatible object storage (MinIO locally) |
| Infra | Docker, Kubernetes + Helm, GitHub Actions, Terraform (present but unverified — no environment has been deployed to yet) |
| AI | Anthropic Claude API (server-side proxy only) |
| Observability | Prometheus, Grafana, Sentry, OpenTelemetry (wired into `main.py`, not yet validated end-to-end) |

## CI Status & Known Issues

Every job in `.github/workflows/ci.yml` is currently failing (or skipped). Root causes found by running the same checks locally against this codebase:

### ❌ Lint & Type Check
- `ruff check apps/api/app/` currently reports **281 errors** (unused imports, un-sorted imports, deprecated `typing.List`/`Optional` usage, lines over 100 chars, etc.).
- `mypy apps/api/app/` reports **55 errors**, mostly from mismatched names between layers (see below).
- `npm run lint` fails immediately — there is **no ESLint config file** anywhere in `apps/web` (no `.eslintrc.*`), so ESLint can't even start.
- `npm run type-check` (`tsc --noEmit`) fails — `tsconfig.json` references `tsconfig.node.json`, which **doesn't exist** in the repo.

### ❌ Unit Tests / Integration Tests
- `pip install -e "apps/api[dev]"` fails outright. `pyproject.toml`'s project name is `saas-platform-api`, but the source lives in `app/` with no `[tool.hatch.build.targets.wheel]` section telling Hatchling what to package — the build backend can't find anything to ship. **This is the first thing that breaks in CI, before a single test runs**, and it also breaks the Docker build (`apps/api/Dockerfile` runs the same `pip install -e` commands).
- Once that's patched locally, the app still fails to import:
  - `app/config.py`'s `Settings` class is missing fields that other modules expect: `DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW`, `effective_read_url`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_REFRESH_TOKEN_EXPIRE_DAYS` (it only defines `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_DAYS`).
  - `app/db/base.py` has no `get_session` function, but it's imported by `dependencies.py`, `routers/v1/auth.py`, and others.
  - `app/core/security.py` defines `decode_token`, but `dependencies.py` imports a non-existent `decode_access_token`. `generate_api_key()` also returns a 3-tuple while its type hint promises 2.
  - `app/services/ai_service.py` exposes plain functions, but `routers/v1/ai.py` imports it as a class, `AIService`, which doesn't exist.
  - `AuthService` only implements `register()` and `authenticate()`, but `routers/v1/auth.py` calls `login()`, `refresh_tokens()`, `setup_mfa()`, `verify_mfa()`, `request_password_reset()`, `confirm_password_reset()` — none of which are implemented.
  - **10 of the 15 SQLAlchemy model files are completely empty** (0 bytes): `activity_log.py`, `api_key.py`, `attachment.py`, `audit_log.py`, `comment.py`, `notification.py`, `organization_member.py`, `sprint.py`, `time_entry.py`, `webhook.py`. Repositories, services, and routers throughout the codebase import specific classes from these files (`Comment`, `Webhook`, `Sprint`, `TimeEntry`, `OrganizationMember`, `Notification`, ...) that don't exist yet.
  - `BaseRepository` only implements `get`, `get_all`, `count`, `create`, `update`, `delete` — but several services (e.g. `AuthService`) call a `.list()` method that was never added.
  - Net effect: `app.main` cannot be imported at all right now, so every integration test and most unit tests fail immediately on collection, independent of any database/Redis service availability.

### ❌ Security Scan
- Trivy's filesystem scan (`severity: HIGH,CRITICAL`, `exit-code: 1`) runs against dependency pins that are roughly two years old at this point (e.g. `python-jose==3.3.0`, `sqlalchemy==2.0.30`, pinned mid-2024). It's likely flagging one or more known HIGH/CRITICAL CVEs in those pins. This needs to be re-run with current dependency versions to get an exact list — it wasn't independently re-verified here since Trivy isn't available in this environment.

### ⏭️ Build Docker Images — Skipped
- This job `needs: [lint, test-unit, test-integration]`. Since all three fail, GitHub Actions skips it by design. It would also fail on its own merits today, since the Dockerfile runs the same broken `pip install -e` step described above.

### ❌ Deploy to Staging
- Fails in ~6 seconds, i.e. at one of the very first steps. Most likely causes: (a) `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` repo secrets aren't configured yet for this prototype, and/or (b) the workflow deploys the image tagged `ghcr.io/<repo>/api:${{ github.sha }}`, which was never built or pushed because the `build` job above is skipped. Confirming which requires access to the Actions run logs/secrets, which weren't available for this review.

### Other repo hygiene notes
- There are a number of stray, empty `.DS_Store`-only directories at the repo root with literal curly braces in their names (e.g. `{apps/{api/{app/...`), left over from a `mkdir -p` command that wasn't brace-expanded correctly. They don't affect CI (no source files inside), but are worth deleting.

## Quick Start

**Note:** given the state above, `make dev` / `make test` will not fully succeed yet — included here as the intended workflow once the issues above are fixed.

```bash
# Clone the repo
git clone git@github.com:Josh200821/Project-management-app.git
cd Project-management-app

# Start local development environment
make dev

# Run database migrations
make migrate

# Run all tests
make test
```

Intended local URLs:
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
│   ├── api/          # FastAPI backend (partially implemented — see Known Issues)
│   └── web/          # React 18 frontend
├── infra/
│   ├── terraform/    # Cloud infrastructure (AWS/Azure/DigitalOcean) — unverified
│   ├── k8s/          # Kubernetes manifests — unverified
│   └── helm/         # Helm chart — unverified
├── packages/
│   └── shared-types/ # Shared TypeScript types
└── .github/
    └── workflows/    # GitHub Actions CI/CD
```

## Intended Architecture

The backend is *designed* around clean architecture with four layers, though the layers aren't fully connected yet (see Known Issues):

```
Router → Service → Repository → Database
```

- No SQL in routers. No business logic in repositories.
- All side effects (emails, webhooks, AI calls) are meant to be dispatched as Celery tasks, never synchronous in the request path.
- Multi-tenancy is intended to be enforced via PostgreSQL Row-Level Security on every tenant-scoped table (`app/core/rls.py` exists but is minimal — 330 bytes — and not yet integrated into request handling).

## Development

### Prerequisites
- Docker & Docker Compose
- Make
- Node.js 20+ (for frontend)
- Python 3.12+ (for local API development without Docker)

### Environment Variables
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

## To-Do List

### ✅ Scaffolded / in place
- [x] Repo layout: `apps/api`, `apps/web`, `infra/`, `packages/shared-types`
- [x] Dependency lists for backend (`pyproject.toml`) and frontend (`package.json`)
- [x] Docker Compose files for dev and test
- [x] GitHub Actions workflows for CI, staging/production deploy, PR previews, security scan
- [x] SQLAlchemy models for `User`, `Organization`, `Project`, `Task` (with Alembic migrations)
- [x] Basic FastAPI routers stubbed for all planned resources (auth, users, orgs, projects, tasks, comments, sprints, attachments, notifications, search, analytics, time entries, webhooks, API keys, billing, AI)
- [x] React app shell: pages, stores (Zustand), API client hooks (React Query), Kanban board components, analytics charts
- [x] Prometheus/Grafana/Sentry/OpenTelemetry wiring started in `main.py`

### 🚧 Currently broken / in progress
- [x] Fix backend packaging (`pyproject.toml` Hatchling config) so `pip install -e apps/api` succeeds
- [x] Reconcile `app/config.py` `Settings` fields with what the rest of the app actually reads (DB pool sizing, JWT settings, read-replica URL)
- [x] Implement `app/db/base.py:get_session` dependency
- [x] Fix `core/security.py` ↔ `dependencies.py` mismatch (`decode_token` vs `decode_access_token`, `generate_api_key` return arity)
- [ ] Fill in the 10 empty SQLAlchemy model files: `ActivityLog`, `ApiKey`, `Attachment`, `AuditLog`, `Comment`, `Notification`, `OrganizationMember`, `Sprint`, `TimeEntry`, `Webhook`
- [ ] Add the missing `BaseRepository.list()` method (or update callers to use `get_all`)
- [ ] Build out `AuthService` to match what `routers/v1/auth.py` expects: `login`, `refresh_tokens`, `setup_mfa`, `verify_mfa`, `request_password_reset`, `confirm_password_reset`
- [ ] Turn `ai_service.py` into the `AIService` class `routers/v1/ai.py` expects (or update the router to call the module functions directly)
- [ ] Add an ESLint config for `apps/web`
- [ ] Add the missing `apps/web/tsconfig.node.json`
- [ ] Clean up the 281 `ruff` findings and 55 `mypy` findings in the API
- [ ] Re-run Trivy locally and update/patch any HIGH/CRITICAL dependency findings
- [ ] Configure staging deploy secrets (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`) and confirm the `build` job actually pushes images before staging deploy is expected to work
- [ ] Get `make dev` to a state where the API boots and `/health` responds
- [ ] Get at least one green CI run end-to-end

### 📋 Not started
- [ ] Row-Level Security policies wired into request/session handling (`core/rls.py` is a stub)
- [ ] OAuth (Google/GitHub/Microsoft) and SAML SSO flows
- [ ] Stripe billing integration beyond schema/env placeholders
- [ ] Load testing pass with Locust (`test-load`)
- [ ] Production deployment (never attempted)
- [ ] OWASP ZAP DAST scan passing against a real staging environment

## API Documentation
Once the backend actually boots:
- Swagger UI: http://localhost:8000/api/docs
- Redoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Security (target state, not fully implemented yet)
- JWT RS256 authentication with rotating refresh tokens
- PostgreSQL Row-Level Security for tenant isolation
- RBAC: Admin, Manager, Member, Viewer roles
- OWASP Top-10 mitigations
- Secrets managed via HashiCorp Vault / AWS Secrets Manager
- OWASP ZAP DAST in CI before production deploys

## License
Not yet decided
