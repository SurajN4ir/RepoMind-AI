# Feature module convention

Each bounded context owns its API handlers, request/response schemas, application services,
repository interfaces and implementations, and persistence models. A module should expose a
single router for composition by `app.api.v1.router`.

```text
modules/<feature>/
├── api/             # HTTP transport: router and route handlers
├── application/     # Use cases and orchestration
├── domain/          # Entities, value objects, and repository ports
├── infrastructure/  # SQLAlchemy models and repository adapters
└── schemas/         # Feature-specific API contracts
```

Do not import another feature's infrastructure directly. Share only deliberately extracted,
framework-independent primitives from `app.core` or `app.utils`.

## Required module documentation

Every module includes a `README.md` before implementation begins. It documents its purpose,
responsibilities, public APIs, dependencies, non-goals, and future work.

## Repository boundary

`BaseRepository` is shared infrastructure for simple CRUD only. Feature modules define their own
repositories for domain-specific queries and name those operations after domain behavior (for
example, `hybrid_search`), rather than extending the generic repository with retrieval behavior.
