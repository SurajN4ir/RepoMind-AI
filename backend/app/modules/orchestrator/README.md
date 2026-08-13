# AI Orchestrator module

## Purpose

Consume bounded `LLMContext` evidence and produce a citation-preserving `GeneratedResponse`.

## Responsibilities

- Build a replaceable `ResponsePlan`.
- Resolve named capabilities through a tool registry.
- Delegate execution to a replaceable workflow engine.
- Invoke a provider-neutral response generator through that workflow.
- Verify citation provenance and expose a transport-neutral stream lifecycle.

## Public API

- `OrchestratorService.respond(LLMContext) -> GeneratedResponse`
- `OrchestratorService.stream(LLMContext) -> AsyncIterator[StreamEvent]`

## Dependencies

- The Context Builder's `LLMContext` domain model.
- Injected workflow engine, generator, tools, verifier, and stream adapter.

## Non-goals

Agent memory, long-term memory, repository indexing, retrieval, query planning, provider-specific
SDKs, or a mandatory LangGraph dependency.

## Future work

Add provider adapters, a LangGraph workflow-engine adapter, richer verifiers, native provider
streaming, and application/API composition at the delivery boundary.
