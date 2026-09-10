# ADR 0015: Legacy ingestion endpoint delegates to the indexing pipeline

## Status

Accepted

## Context

`POST /repositories/{id}/ingest` predates `RepositoryIndexingPipeline`
(ADR-0006 through ADR-0010 describe the pipeline's constituent stages). It
was backed by its own `IngestionService`/`IngestionApplicationService`,
which independently re-implemented "clone, walk, build a manifest,
transition Repository status" using the same low-level primitives
(`GitClient`, `RepositoryWalker`, `RepositoryFileFilter`) that
`RepositoryIndexingPipeline` also uses internally. Once the pipeline existed
and became the path every real indexing request uses
(`POST .../index`), this endpoint was two independent orchestrations of
overlapping work: the same repository could be cloned and walked
differently by whichever endpoint a caller hit, workspace cleanup and status
transitions were maintained in two places, and Phase 3 ownership
enforcement had to be threaded through both instead of one.

Deleting the endpoint outright was rejected: it is a public, documented API
contract, and removing it without a caller audit risks breaking existing
integrations for no benefit proportional to the risk.

## Decision

`POST /repositories/{id}/ingest` becomes a thin adapter over
`RepositoryIndexingPipeline` -- the same dependency `POST .../index` uses.
It runs the full pipeline (clone, walk, parse, chunk, embed, index) and
reports only the manifest portion of the result, preserving its original
response contract. `IngestionService` and `IngestionApplicationService` are
removed; there is no longer a second orchestration of clone+walk+manifest+
status-transition. The route is marked `deprecated=True` in its OpenAPI
metadata. New integrations should call `POST .../index` directly.

## Consequences

- One canonical indexing/ingestion implementation. Any change to cloning,
  parsing, chunking, embedding, or indexing behavior applies uniformly to
  both endpoints, because there is only one code path.
- `POST .../ingest` now does strictly more work per call than it used to
  (the full pipeline, not just a manifest walk); callers relying on it being
  a cheap, side-effect-free manifest preview will notice the added latency
  and the new indexing side effects (pgvector writes, status transitions to
  the full set the pipeline can reach, embedding provider calls).
- `RepositoryManifest` (ADR-0006) remains an accurate description of the
  pipeline's internal handoff contract between its clone/walk stage and
  parsing; what changed is that a manifest is no longer the *final* output
  of a standalone, independently-invokable HTTP step.
- Phase 3's `AuthorizedRepositoryDependency` gate is unchanged and applies
  identically to both endpoints, since both now depend on the same
  authorization dependency ahead of the same pipeline dependency.
