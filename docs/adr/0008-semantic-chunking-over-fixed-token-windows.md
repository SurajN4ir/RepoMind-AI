# ADR 0008: Prefer semantic chunking over fixed token windows

## Status

Accepted

## Context

Future repository search quality depends on chunks retaining meaningful code and documentation
boundaries. Fixed-size token windows split declarations unpredictably and discard useful symbol,
import, export, parent, and line-range context.

## Decision

The Semantic Chunker consumes `ParsedRepository` only and creates chunks at parser-declared symbol
boundaries, Markdown heading sections, configuration sections, or whole-file generic-text
boundaries. Token counts are recorded but never used as a splitting rule. Chunk IDs are
deterministic hashes of stable repository, file, symbol, range, and type information.

## Consequences

- Retrieval consumers receive chunks with stable semantic identities and rich metadata.
- Strategies can evolve per language without changing the parser or embedding pipeline.
- Very large semantic declarations remain intact; any future size policy must be an explicit,
  separately documented decision.
