# ADR 0005: Keep repository lifecycle separate from ingestion implementation

## Status

Accepted

## Context

The first business bounded context registers source-code repositories. Future work will clone,
parse, chunk, and index their contents. Exposing those worker steps in the Repository domain would
couple metadata ownership to a specific ingestion implementation.

## Decision

The Repository module owns only repository metadata and the lifecycle states `NEW`, `REGISTERED`,
`INDEXING`, `READY`, `FAILED`, and `ARCHIVED`. It neither imports nor invokes an Ingestion module.
Future ingestion work will request lifecycle updates through the Repository service's public
status-update operation.

## Consequences

- Repository routes do not expose clone or ingest operations.
- Ingestion can evolve its internal phases without a Repository schema change.
- Repository-level status remains a stable, concise representation for API consumers.
