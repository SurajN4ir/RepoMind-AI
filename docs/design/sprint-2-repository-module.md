# Sprint 2 design: Repository module

## Status

Implemented in Sprint 2. This document remains the boundary contract for the module.

## Purpose

The Repository module manages the metadata and lifecycle state of one registered Git repository.
It is the system of record for repository registration. It does not clone, inspect, parse, chunk,
embed, or otherwise ingest repository content.

## Responsibilities

- Register a repository record.
- Prevent duplicate registrations.
- Validate its URL, provider, and default branch.
- Read repository metadata and lifecycle status.
- Update supported repository metadata and status.
- Delete or archive a repository record according to the chosen API contract.

## Non-goals

- Git cloning or provider API calls.
- Ingestion orchestration, parsing, chunking, embeddings, or RAG.
- File, symbol, chunk, token, or embedding counts.
- Authentication and authorization policy.

## Proposed module boundary

```text
app/modules/repository/
├── README.md
├── models.py
├── schemas.py
├── repository.py
├── service.py
├── routes.py
├── enums.py
└── exceptions.py
```

The module will depend on `app.shared.database` for persistence primitives only. Its repository
adapter may subclass `BaseRepository` for simple CRUD, but any repository-specific queries remain
local to this module.

## Data model

Table: `repositories`

| Field | Type / constraint | Notes |
| --- | --- | --- |
| `id` | UUID primary key | Shared UUID mixin. |
| `name` | non-empty string | Display name. |
| `url` | unique URL | Canonical registration address. |
| `provider` | `RepositoryProvider` enum | GitHub, GitLab, Bitbucket, or local. |
| `default_branch` | non-empty string | Branch metadata only. |
| `status` | `RepositoryStatus` enum | Lifecycle state, not ingestion steps. |
| `description` | nullable string | Optional repository metadata. |
| `language_summary` | nullable JSON-compatible value | Optional summary only; no analysis work in this module. |
| `last_indexed_at` | nullable UTC timestamp | Set by a future ingestion integration after successful indexing. |
| `created_at` | UTC timestamp | Shared timestamp mixin. |
| `updated_at` | UTC timestamp | Shared timestamp mixin. |

## Lifecycle

```text
NEW → REGISTERED → INDEXING → READY
                    └──────→ FAILED
READY or FAILED → ARCHIVED
```

The values describe repository-level lifecycle state. They deliberately avoid implementation
details such as cloning, scanning, chunking, and embedding.

## Enumerations

`RepositoryProvider`: `GITHUB`, `GITLAB`, `BITBUCKET`, `LOCAL`.

`RepositoryStatus`: `NEW`, `REGISTERED`, `INDEXING`, `READY`, `FAILED`, `ARCHIVED`.

## Proposed HTTP API

| Method | Path | Responsibility |
| --- | --- | --- |
| `POST` | `/api/v1/repositories` | Register a repository. |
| `GET` | `/api/v1/repositories` | List repositories with shared pagination. |
| `GET` | `/api/v1/repositories/{id}` | Retrieve one repository. |
| `PATCH` | `/api/v1/repositories/{id}` | Update allowed metadata or lifecycle status. |
| `DELETE` | `/api/v1/repositories/{id}` | Delete the repository record. |

No ingestion endpoint is part of Sprint 2.

## Invariants and validation

- URL is required, structurally valid, and unique.
- Provider is one of the supported enum values.
- Default branch is required and non-blank.
- Status changes must comply with the lifecycle policy defined during implementation.
- Domain validation belongs in the service; persistence constraints protect integrity.

## Future interaction

A future Ingestion module may request a status update through the Repository module's public
application service. The Repository module must not import or orchestrate Ingestion.

## Implementation checklist

1. Create the module README using the required module documentation convention.
2. Confirm lifecycle transition policy and PATCH field permissions.
3. Define API schemas and error mapping.
4. Implement model, repository adapter, service, routes, migration, and tests.
5. Add an ADR only if the implementation changes a durable architectural decision.
