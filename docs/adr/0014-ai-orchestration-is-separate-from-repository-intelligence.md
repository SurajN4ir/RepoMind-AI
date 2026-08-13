# ADR 0014: Keep AI orchestration separate from repository intelligence

## Status

Accepted

## Context

Repository intelligence already plans user requests, retrieves evidence, and constructs bounded,
cited context. Those capabilities remain useful without an LLM. Coupling them to a workflow graph
or a response provider would make their deterministic behavior harder to reuse and test.

## Decision

Introduce an Orchestrator bounded context that consumes `LLMContext` and produces
`GeneratedResponse`. Response planning, tools, workflow execution, response generation,
verification, and streaming are replaceable abstractions. LangGraph, if adopted, will be an
adapter behind `WorkflowEngine` rather than a system-wide dependency.

## Consequences

- Repository intelligence exists without AI; AI consumes repository intelligence.
- Provider and workflow changes remain isolated to the orchestrator composition boundary.
- Generated responses retain evidence citations without exposing private reasoning traces.
