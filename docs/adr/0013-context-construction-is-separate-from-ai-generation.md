# ADR 0013: Keep context construction separate from AI generation

## Status

Accepted

## Context

Retrieval hits are ranked search records, while a reasoning system needs coherent, cited, bounded
evidence. Letting an agent decide formatting, pruning, and token limits would duplicate policy,
make context size unpredictable, and tightly couple search evidence to one model provider.

## Decision

Introduce a Context Builder bounded context. It transforms `RetrievedContext` into structured
`LLMContext` by pruning, ordering, grouping, budgeting, and formatting evidence through
replaceable policies. It makes no LLM calls and owns no prompt template.

## Consequences

- Future agents receive consistently bounded, traceable evidence.
- Token counting and formatting can change without altering retrieval or orchestration.
- The same evidence context can serve non-LLM consumers such as reports or UI views.
