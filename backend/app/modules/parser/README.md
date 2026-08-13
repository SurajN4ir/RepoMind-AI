# Semantic Parser module

## Purpose

Transform a `RepositoryManifest` plus its ephemeral source root into language-agnostic semantic
domain models for Python, JavaScript, and TypeScript.

## Responsibilities

- Detect supported source languages.
- Parse supported files with Tree-sitter.
- Extract classes, functions, methods, imports, exports, docstrings, and comments.
- Preserve the Tree-sitter AST internally on each `ParsedFile`.
- Retain source internally on each `ParsedFile` so downstream semantic consumers never re-read files.
- Continue after individual file failures and record the error on that file.

## Dependencies

- Ingestion manifest domain objects.
- Tree-sitter grammar bindings for Python, JavaScript, and TypeScript.
- An explicit ephemeral source root containing the manifest's relative file paths.

## Non-goals

- Chunking, embeddings, vector storage, retrieval, LangGraph, AI, chat, persistence, or API routes.
- Determining chunk boundaries or retaining source contents outside the active parse workflow.

## Future work

- A separate chunking module can consume `ParsedRepository` and apply product-specific boundaries.
- Future orchestration can invoke parsing before the ingestion workspace is cleaned up.
