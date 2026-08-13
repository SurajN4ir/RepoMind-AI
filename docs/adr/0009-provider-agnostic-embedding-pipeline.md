# ADR 0009: Use a provider-agnostic embedding pipeline

## Status

Accepted

## Context

Embedding models and vendors change frequently, while RepoMind's semantic chunks and indexing
contracts must remain stable. Allowing a provider to receive Chunk objects would couple vendor
formatting and transport behavior to repository-domain semantics.

## Decision

The embedding pipeline transforms chunks into provider-neutral `IndexDocument` objects. Providers
implement a minimal asynchronous `EmbeddingProvider` protocol that accepts only documents and
returns vectors. Ollama is the initial adapter, while batching, retry policy, normalization, and
collection assembly remain provider-independent.

## Consequences

- New vendors can be added without changing the embedding service or chunker.
- Provider-specific HTTP, request payloads, and response validation stay isolated.
- Vector persistence and retrieval remain independent future bounded contexts.
