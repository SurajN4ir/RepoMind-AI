# Indexing module

## Purpose

Synchronize `EmbeddingCollection` output into provider-swappable vector, keyword, and metadata
write-side index projections.

## Responsibilities

- Convert embedding documents and vectors into canonical deterministic `IndexEntry` records.
- Plan inserts, updates, unchanged records, and deletions from stable content hashes.
- Atomically synchronize vector, keyword, and metadata storage ports.
- Return indexing statistics and a logical `RepositoryIndex` result.

## Dependencies

- Embedding Pipeline domain models.
- Vector, keyword, metadata, and transaction storage ports.

## Non-goals

- Retrieval, query processing, hybrid ranking, result assembly, LangGraph, or AI chat.
- Selecting a concrete vector, keyword, or metadata storage product.

## Future work

- Add production adapters for pgvector/PostgreSQL FTS, Qdrant, Milvus, Weaviate, BM25, or
  OpenSearch.
- Add a separate Retrieval bounded context that reads from these ports.
