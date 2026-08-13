# ADR 0003: Use async-first shared persistence infrastructure

## Status

Accepted

## Context

RepoMind's API serves I/O-bound workflows and will rely on PostgreSQL through Supabase. Database
infrastructure should not force future feature modules into synchronous blocking calls or expose
SQLAlchemy exceptions outside the persistence boundary.

## Decision

Use SQLAlchemy 2.0's async engine and `AsyncSession` throughout shared persistence infrastructure.
Feature modules receive sessions through dependency injection and use a generic `BaseRepository`
for uncomplicated CRUD mechanics. Transaction boundaries are explicit through an async context
manager. UUID and timestamp mixins provide consistent technical fields without defining product
models.

Alembic runs through SQLAlchemy's async-engine bridge while retaining Alembic's synchronous
migration API internally.

## Consequences

- Feature application services must be async when accessing persistence.
- Business code receives persistence-neutral exceptions instead of SQLAlchemy implementation errors.
- Connection pools are disposed during ASGI shutdown.
