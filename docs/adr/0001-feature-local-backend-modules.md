# ADR 0001: Organize backend code by bounded feature

## Status

Accepted

## Context

RepoMind will grow across multiple independent product capabilities. Layer-only top-level
directories such as `services`, `repositories`, and `models` make a feature's implementation
scatter across the codebase and increase accidental coupling.

## Decision

Business code will live under `backend/app/modules/<feature>`. Each module owns its API transport,
application use cases, domain contracts, schemas, and infrastructure adapters. The versioned API
composition root imports a module's public router only.

`app.core`, `app.config`, `app.shared`, `app.dependencies`, `app.middleware`, and `app.utils` are
reserved for intentionally shared technical concerns. They must not become a home for feature
business logic.

## Consequences

- Features can evolve, test, and eventually deploy with clearer boundaries.
- Cross-feature imports require deliberate extraction of a shared abstraction.
- Some small duplication is preferred over premature shared service or repository layers.
