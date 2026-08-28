# ── Base ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libmagic1 libxmlsec1-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# ── Dependencies ──────────────────────────────────────────────────────
FROM base AS dependencies
COPY pyproject.toml .
RUN pip install -e ".[dev]"

# ── Development ───────────────────────────────────────────────────────
FROM dependencies AS development
COPY . .
RUN mkdir -p /app/keys
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production ────────────────────────────────────────────────────────
FROM base AS production
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY pyproject.toml .
RUN pip install -e "." --no-deps
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
EXPOSE 8000
