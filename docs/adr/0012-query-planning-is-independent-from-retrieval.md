# ADR 0012: Keep query planning independent from retrieval

## Status

Accepted

## Context

Understanding a request involves intent classification, repository selection, validation, and
filter extraction. Retrieval is a read-side concern that should only execute an already formed
`SearchQuery`. Combining these responsibilities would make search storage and ranking depend on
request-language policy.

## Decision

Introduce a Query Engine bounded context that produces `QueryPlan` and `SearchQuery` values. It
uses deterministic, replaceable intent detection and a repository-resolution port, but never
depends on `RetrievalService`, LLMs, prompts, or context assembly.

## Consequences

- Retrieval remains focused on searching and ranking evidence.
- Request understanding can evolve independently, including future ML-backed intent detection.
- Plans are easy to validate and test before any read-side storage is called.
