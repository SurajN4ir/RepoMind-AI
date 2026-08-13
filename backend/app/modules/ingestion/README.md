# Ingestion module

## Purpose

Create a disposable local workspace for a registered repository and produce a clean file manifest.

## Responsibilities

- Perform a depth-one Git clone into a temporary workspace.
- Apply configurable directory, binary, and file-size filtering.
- Walk accepted files and return pure `RepositoryManifest` domain objects.
- Transition Repository status through `RepositoryService` only.
- Remove temporary workspaces on success and failure.

## Public API

- `POST /api/v1/repositories/{id}/ingest`

## Dependencies

- Repository module service for repository metadata and lifecycle transitions.
- Shared UTC clock for manifest timestamps.
- Local Git executable, filesystem, and temporary workspace facilities.

## Non-goals

- Tree-sitter, parsing, chunking, embeddings, vector storage, retrieval, LangGraph, AI, chat,
  or documentation generation.
- Persisting manifests or file records.
- Provider API calls beyond `git clone`.

## Future work

- A separate parsing/chunking module may consume the manifest as an input contract.
- Persist manifest metadata only if a future bounded context explicitly requires it.
