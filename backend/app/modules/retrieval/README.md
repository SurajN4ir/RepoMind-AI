# Retrieval module

## Purpose

Read indexed repository data through provider- and storage-agnostic ports, then return ordered,
cited `RetrievedContext` objects.

## Responsibilities

- Embed a `SearchQuery` through the existing embedding-provider protocol.
- Run vector and keyword lookup concurrently.
- Fuse ranked lists using configurable Reciprocal Rank Fusion.
- Apply metadata filters, deduplicate chunk IDs, paginate, and assemble citations.

## Dependencies

- Embedding provider protocol for query vectors.
- Vector, keyword, and metadata read-side storage ports.

## Non-goals

- Index writes, LLM calls, prompts, conversation memory, agent planning, LangGraph, chat, or
  response generation.

## Future work

- Add concrete pgvector, PostgreSQL FTS, Qdrant, OpenSearch, and similar read adapters.
- Add an optional reranking strategy as a separate, explicitly configured read-side stage.
