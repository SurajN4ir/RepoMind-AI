# Context Builder module

## Purpose

Transform `RetrievedContext` into bounded, structured `LLMContext` evidence for any future
reasoning system.

## Responsibilities

- Preserve citations while enriching results into evidence chunks.
- Prune duplicate, nested, and trivial snippets.
- Order evidence coherently by source file and line.
- Group evidence into file sections, apply a token budget, and format source evidence.
- Report auditable construction statistics.

## Public API

`ContextBuilderService.build(RetrievedContext) -> LLMContext`

## Dependencies

- Retrieval-domain value objects only.

## Non-goals

LLM calls, prompt templates, chat, memory, LangGraph, agent orchestration, and retrieval itself.

## Future work

Introduce model-specific token counters, semantic/module grouping, optional section summaries, and
application-specific presentation formatters behind the existing policy interfaces.
