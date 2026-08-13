# Semantic Chunker module

## Purpose

Convert a `ParsedRepository` into deterministic, rich, transient semantic chunks.

## Responsibilities

- Consume parser domain models only; never open raw repository files.
- Use language- and file-type-specific semantic boundary strategies.
- Build stable chunk identifiers and retrieval-oriented metadata.
- Estimate token counts through a replaceable tokenizer abstraction.

## Dependencies

- Parser domain models, including internally retained parser source.
- Shared UUID and UTC primitives through upstream domain objects.

## Non-goals

- Fixed token windows, embeddings, vector storage, retrieval, persistence, LangGraph, AI, or chat.
- Re-parsing source files or deciding how chunks are embedded.

## Future work

- A separate embedding/indexing module can consume `ChunkCollection`.
- A model-specific tokenizer can replace `EstimatingTokenizer` without changing strategies.
