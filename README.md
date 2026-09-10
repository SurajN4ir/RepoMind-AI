# RepoMind

[![CI](https://github.com/SurajN4ir/RepoMind-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/SurajN4ir/RepoMind-AI/actions/workflows/ci.yml)

RepoMind is an AI-powered repository intelligence platform that enables developers to understand and interact with codebases through natural language queries. It provides semantic understanding of repositories, intelligent search capabilities, and automated code analysis.

## Key Features

- **Semantic Code Search**: Query your codebase using natural language
- **Repository Intelligence**: Automated analysis of code structure and dependencies
- **AI Orchestration**: Unified AI pipeline for repository understanding
- **Context Construction**: Intelligent context building for AI models
- **Hybrid Retrieval**: Combines vector and keyword-based retrieval
- **Provider Agnostic Embeddings**: Supports multiple embedding providers

## Architecture

RepoMind is composed of:
1. **Backend API** - FastAPI-based server with AI orchestration capabilities
2. **Frontend UI** - React-based interface for querying and visualizing repository intelligence
3. **Repository Intelligence Module** - Core module for understanding codebases
4. **AI Pipeline** - Orchestration layer for managing AI operations

## Documentation

- [Product UI/UX Blueprint](docs/product-ui-ux-blueprint.md)
- [Frontend Architecture](docs/frontend-architecture.md)
- [ADR - Architectural Decision Records](docs/adr/)
- [Design Docs](docs/design/)

## Continuous Integration

`.github/workflows/ci.yml` runs on every push to `main` and every pull
request. It validates the backend and frontend independently:

- **Backend**: `ruff check backend`, `alembic upgrade head` against a fresh
  PostgreSQL+pgvector service container (validating the full `0001 -> head`
  migration chain), then the full test suite with `TEST_DATABASE_URL` set so
  the pgvector integration tests run for real instead of skipping.
- **Frontend**: `npm run typecheck`, `npm run lint`, `npm run build`.

Local equivalents:

```bash
# Backend (requires a reachable PostgreSQL+pgvector for TEST_DATABASE_URL)
uv run ruff check backend
DATABASE_URL=<your-postgres-url> uv run alembic upgrade head
TEST_DATABASE_URL=<your-postgres-url> uv run pytest backend/tests -v

# Frontend
cd frontend
npm run typecheck
npm run lint
npm run build
```

## Getting Started (Docker)

Verified end-to-end: `docker compose up` brings up PostgreSQL+pgvector, runs
migrations, starts the backend, and starts the frontend, in that order.

### Prerequisites

- Docker and Docker Compose
- [Ollama](https://ollama.com) running on your host machine (RepoMind does not
  containerize it), with the models you intend to use pulled:
  ```bash
  ollama pull all-minilm:l6-v2   # embeddings
  ollama pull llama3.2           # response generation
  ```

### Environment variables

```bash
cp .env.example .env
```

`.env.example` is documented inline. The two things you'll actually need to
decide:

- **Database**: the default `DATABASE_URL` points at the `postgres` service
  Compose starts for you. To use a hosted PostgreSQL/Supabase database
  instead, just replace `DATABASE_URL` with your connection string — nothing
  else changes, and the local `postgres` service is simply left unused.
- **Frontend auth (Clerk)**: without `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and
  `CLERK_SECRET_KEY` (get them at https://dashboard.clerk.com), the frontend
  container starts but every page returns 500. Backend functionality and the
  API are unaffected either way.

If ports 8000 or 3000 are already in use on your machine, override them:
`BACKEND_PORT=8010 FRONTEND_PORT=3010` in `.env`.

### Start RepoMind

```bash
docker compose up -d --build
```

This starts, in dependency order:

1. `postgres` — PostgreSQL 16 with the pgvector extension, backed by a named
   volume (`postgres_data`) so data survives restarts. Compose waits for its
   healthcheck (`pg_isready`) before starting the backend.
2. `backend` — on container start, runs `alembic upgrade head` against
   `postgres`, then starts the API. Compose waits for `/api/health/ready`
   (which checks real database connectivity, not just process liveness)
   before starting the frontend.
3. `frontend` — Next.js, served standalone.

Check status: `docker compose ps`. Logs: `docker compose logs -f backend`.

### How migrations work

Migrations run automatically on backend container startup (see the
Dockerfile) — this is a local/dev convenience, not a production
release-migration strategy. To run them manually against a running stack:

```bash
docker compose exec backend alembic upgrade head
```

### Stopping / resetting

```bash
docker compose down       # stop containers, keep the database volume
docker compose down -v    # stop containers AND delete the database volume
```

To verify from a completely clean database, `docker compose down -v` then
`docker compose up -d --build` again.

## Getting Started (native, without Docker)

Backend: see `backend/pyproject.toml` for dependencies (installed via
[uv](https://docs.astral.sh/uv/)); point `DATABASE_URL` in `backend/.env` at
either a local SQLite file or a reachable PostgreSQL instance, then run
`uvicorn app.main:create_app --factory --app-dir backend`.

Frontend: `cd frontend && npm install && npm run dev`.