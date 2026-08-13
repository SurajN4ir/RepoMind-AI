# ADR 0011: Prefer hybrid retrieval over vector-only lookup

## Status

Accepted

## Context

Code repositories contain exact identifiers, paths, symbols, and configuration keys alongside
semantic concepts. Vector-only retrieval can miss exact terminology, while keyword-only retrieval
misses related concepts expressed differently.

## Decision

The Retrieval module queries vector and keyword read ports in parallel, then combines their ranked
lists using configurable Reciprocal Rank Fusion. Metadata filtering runs on the fused results and
the module returns ordered context with citations. No retrieval stage writes indexes or invokes an
LLM.

## Consequences

- Exact identifier matching and semantic similarity both influence context selection.
- Storage engines remain replaceable behind independent read-side ports.
- Ranking policy stays isolated from indexing transactions and agent orchestration.
