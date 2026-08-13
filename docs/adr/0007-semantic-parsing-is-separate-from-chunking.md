# ADR 0007: Keep semantic parsing separate from chunking

## Status

Accepted

## Context

Tree-sitter parsing provides language-specific syntax and declarations. Chunking is a downstream
product policy that may vary by model, retrieval strategy, token budget, or user experience.
Combining the two would make parser output dependent on unstable downstream decisions.

## Decision

The Semantic Parser consumes a repository manifest and ephemeral source root, then produces pure,
language-agnostic `ParsedRepository` models. It extracts semantic metadata and retains ASTs only
internally. It does not choose chunk boundaries or persist output.

## Consequences

- Parsing can be reused by different future chunking policies.
- Syntax failures remain isolated to a `ParsedFile` instead of aborting a repository parse.
- The parser remains independent of embeddings, vector stores, and retrieval concerns.
