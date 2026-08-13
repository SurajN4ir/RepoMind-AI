# ADR 0006: Ingestion produces manifests, not parsed chunks

## Status

Accepted

## Context

Repository workspace preparation needs a stable handoff to future parsing and indexing work.
Combining Git workspace operations with parsing or chunking would make file-selection policy depend
on language tooling and would couple an I/O-heavy concern to future AI-oriented behavior.

## Decision

The Ingestion module shallow-clones a repository, filters and inventories files, then returns a
pure `RepositoryManifest`. The manifest contains selected file metadata and aggregate selection
statistics only. It does not retain content, syntax trees, chunks, embeddings, or vectors.

## Consequences

- File filtering and workspace cleanup can be tested independently of language tooling.
- Future parsing/chunking modules consume a narrow, versioned contract.
- Manifest persistence is deferred until a bounded context has a concrete use for it.
