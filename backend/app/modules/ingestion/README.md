# Ingestion module

## Purpose

Provide the low-level primitives for turning a registered repository into a
local, filtered file inventory: a depth-one Git clone and a pure
`RepositoryManifest` domain object. This module does not orchestrate an
ingestion workflow itself.

## Responsibilities

- Perform a depth-one Git clone (`GitClient`).
- Apply configurable directory, binary, and file-size filtering
  (`RepositoryFileFilter`, `IngestionFilterConfig`).
- Walk accepted files and return pure `RepositoryManifest` domain objects
  (`RepositoryWalker`).
- Serialize manifests for HTTP responses (`RepositoryManifestResponse`).

## Who orchestrates this

`RepositoryIndexingPipeline` (`backend/app/application/pipelines/repository_indexing_pipeline.py`)
is the canonical caller: it owns workspace lifecycle, repository status
transitions, and error recovery, then continues on to parsing, chunking,
embedding, and indexing. This module does not manage workspace cleanup or
Repository status itself -- an earlier `IngestionService` did, as a
standalone orchestrator reachable only via `POST .../ingest`; it duplicated
what the pipeline does and was removed (see
`docs/adr/0015-legacy-ingestion-endpoint-delegates-to-indexing-pipeline.md`).

## Public API

- `POST /api/v1/repositories/{id}/ingest` -- deprecated; a thin adapter that
  runs the canonical pipeline and reports only its manifest. See
  `app/api/v1/routes/legacy_ingestion.py`.

## Dependencies

- Local Git executable and filesystem.
- Shared UTC clock for manifest timestamps.

## Non-goals

- Tree-sitter, parsing, chunking, embeddings, vector storage, retrieval, LangGraph, AI, chat,
  or documentation generation.
- Persisting manifests or file records.
- Provider API calls beyond `git clone`.
- Workspace lifecycle and Repository status transitions (owned by
  `RepositoryIndexingPipeline`).
