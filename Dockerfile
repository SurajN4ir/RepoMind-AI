FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# git is required at runtime: RepositoryIndexingPipeline shells out to it to
# clone repositories (app/modules/ingestion/git.py). python:3.13-slim doesn't
# include it.
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY alembic.ini ./alembic.ini
COPY backend ./backend

EXPOSE 8000

# --app-dir backend: the app package lives at ./backend/app, not ./app --
# WORKDIR stays /app so alembic.ini's `script_location = backend/alembic`
# resolves correctly. Migrations run before the server starts so a fresh
# database is always ready; this is the local/dev startup path, not a
# production release-migration strategy.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --app-dir backend"]
