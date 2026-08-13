# Embedding module

## Purpose

Convert transient semantic `ChunkCollection` output into normalized, provider-agnostic embedding
vectors.

## Responsibilities

- Transform chunks into provider-facing `IndexDocument` objects.
- Batch documents with stable ordering and estimated token budgets.
- Call an injected provider interface and retry transient batch failures.
- Normalize vectors and return `EmbeddingCollection` domain models.

## Dependencies

- Semantic Chunker domain models.
- A provider implementing the `EmbeddingProvider` protocol.
- `httpx` only within the Ollama adapter.

## Non-goals

- Database persistence, pgvector, vector indexes, keyword indexes, search, retrieval, LangGraph,
  AI chat, query planning, or provider selection from application configuration.

## Future work

- Add provider adapters for OpenAI, Voyage, Jina, BGE, or other supported vendors.
- Add an indexing bounded context that persists `EmbeddingCollection` independently of retrieval.
