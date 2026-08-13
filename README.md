# RepoMind

RepoMind is an AI-powered repository intelligence platform that enables developers to understand and interact with codebases through natural language queries. It provides semantic understanding of repositories, intelligent search capabilities, and automated code analysis.

## Key Features

- **Semantic Code Search**: Query your codebase using natural language
- **Repository Intelligence**: Automated analysis of code structure and dependencies
- **AI Orchestration**: Unified AI pipeline for repository understanding
- **Context Construction**: Intelligent context building for AI models
- **Hybrid Retrieval**: Combines vector and keyword-based retrieval
- **Provider Agnostic Embeddings**: Supports multiple embedding providers

## Architecture

RepoMind is composed of:
1. **Backend API** - FastAPI-based server with AI orchestration capabilities
2. **Frontend UI** - React-based interface for querying and visualizing repository intelligence
3. **Repository Intelligence Module** - Core module for understanding codebases
4. **AI Pipeline** - Orchestration layer for managing AI operations

## Documentation

- [Product UI/UX Blueprint](docs/product-ui-ux-blueprint.md)
- [Frontend Architecture](docs/frontend-architecture.md)
- [ADR - Architectural Decision Records](docs/adr/)
- [Design Docs](docs/design/)

## Getting Started

1. Clone the repository
2. Set up environment variables (`cp .env.example .env`)
3. Install dependencies (`pip install -r requirements.txt` and `npm install`)
4. Run the application (`uvicorn backend.main:app --reload` for backend, `npm run dev` for frontend)