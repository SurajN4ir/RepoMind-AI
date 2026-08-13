# Repository module

## Purpose

Own metadata and lifecycle state for a registered source-code repository.

## Responsibilities

- Register, retrieve, list, update, and delete repository records.
- Validate provider, URL, duplicate URL, and lifecycle status transitions.
- Expose the `/api/v1/repositories` HTTP API.

## Public API

- `POST /api/v1/repositories`
- `GET /api/v1/repositories`
- `GET /api/v1/repositories/{id}`
- `PATCH /api/v1/repositories/{id}`
- `DELETE /api/v1/repositories/{id}`

## Dependencies

- `app.shared.database` for async sessions, transactions, base repository, pagination, and mixins.
- FastAPI and Pydantic for HTTP transport and request/response contracts.

## Non-goals

- Cloning or calling Git/provider APIs.
- Indexing, parsing, chunking, embeddings, retrieval, AI agents, or chat.
- Ownership of files, symbols, chunks, or ingestion statistics.

## Future work

- Integrate with a separate Ingestion bounded context through `RepositoryService.update_status`.
- Introduce authorization around repository ownership once authentication exists.
