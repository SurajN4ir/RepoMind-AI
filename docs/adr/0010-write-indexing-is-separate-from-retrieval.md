# ADR 0010: Keep write-side indexing separate from retrieval

## Status

Accepted

## Context

Embedding output needs durable, idempotent synchronization into vector, keyword, and metadata
projections. Query-time ranking and context assembly have different performance, consistency, and
product concerns from index writes.

## Decision

The Indexing module is a write-only concern. It consumes `EmbeddingCollection`, computes
deterministic content hashes, and synchronizes storage ports atomically. It exposes no search or
query API. A future Retrieval module will depend on read-side ports and can evolve independently.

## Consequences

- Incremental writes avoid unnecessary re-indexing.
- Storage technologies can be changed without changing query-time behavior.
- Retrieval policies cannot accidentally influence persistence or transaction semantics.
