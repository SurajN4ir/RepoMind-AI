# ADR 0002: Keep runtime configuration and infrastructure at the application boundary

## Status

Accepted

## Context

The platform needs environment-specific configuration and will use Supabase PostgreSQL. Domain
code must remain independent of process environment and database connection details.

## Decision

Pydantic Settings is the single runtime configuration source. SQLAlchemy engine/session setup and
Alembic migration configuration stays in `app.shared.database` and `backend/alembic`. It is constructed
lazily and injected at HTTP/application boundaries when needed.

## Consequences

- Tests can replace infrastructure through dependency injection.
- Importing application code has no database side effects.
- Modules depend on repository ports rather than directly on a global session factory.
