# Query Engine module

## Purpose

Convert a user request into a validated `QueryPlan` containing the shared retrieval `SearchQuery`.

## Responsibilities

- Normalize and validate requests.
- Detect intent using a replaceable, rule-based detector.
- Resolve repository scope through a read-only port.
- Extract supported metadata filters and planning warnings.

## Public API

`QueryEngineService.plan(UserRequest) -> QueryPlan`

## Dependencies

- The retrieval module's `SearchQuery` value object.
- A `RepositoryResolver` read port supplied by the application composition root.

## Non-goals

Retrieval, LLM calls, prompts, LangGraph, context assembly, chat, and agent orchestration.

## Future work

Provide a Repository-module resolver adapter, richer syntax-aware filters, and an ML/LLM intent
detector behind the existing `IntentDetector` protocol.
