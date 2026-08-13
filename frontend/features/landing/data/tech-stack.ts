/**
 * features/landing/data/tech-stack.ts
 *
 * Technology stack data for the "Tech Stack" landing section.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type TechCategory = "backend" | "frontend" | "ai" | "infrastructure";

export interface TechItem {
  id: string;
  name: string;
  category: TechCategory;
  description: string;
  /** URL-safe badge color hint */
  color: string;
}

// ---------------------------------------------------------------------------
// Category labels and colors
// ---------------------------------------------------------------------------

export const CATEGORY_LABELS: Record<TechCategory, string> = {
  backend: "Backend",
  frontend: "Frontend",
  ai: "AI / ML",
  infrastructure: "Infrastructure",
};

export const CATEGORY_COLORS: Record<TechCategory, string> = {
  backend: "bg-primary/10 text-primary border-primary/20",
  frontend: "bg-accent/10 text-accent border-accent/20",
  ai: "bg-success/10 text-success border-success/20",
  infrastructure: "bg-warning/10 text-warning border-warning/20",
};

// ---------------------------------------------------------------------------
// Stack definition
// ---------------------------------------------------------------------------

export const TECH_STACK: TechItem[] = [
  // Backend
  { id: "python", name: "Python 3.12", category: "backend", description: "Core application runtime", color: "primary" },
  { id: "fastapi", name: "FastAPI", category: "backend", description: "Async REST API layer", color: "primary" },
  { id: "treesitter", name: "Tree-sitter", category: "backend", description: "AST-based code parser", color: "primary" },
  { id: "pydantic", name: "Pydantic v2", category: "backend", description: "Data validation and settings", color: "primary" },
  { id: "sqlalchemy", name: "SQLAlchemy", category: "backend", description: "Database ORM", color: "primary" },

  // AI / ML
  { id: "openai", name: "OpenAI", category: "ai", description: "LLM provider (replaceable)", color: "success" },
  { id: "pgvector", name: "pgvector", category: "ai", description: "Vector similarity in Postgres", color: "success" },
  { id: "qdrant", name: "Qdrant", category: "ai", description: "High-perf vector search engine", color: "success" },
  { id: "langchain", name: "LangChain", category: "ai", description: "LLM orchestration primitives", color: "success" },

  // Frontend
  { id: "nextjs", name: "Next.js 15", category: "frontend", description: "React App Router framework", color: "accent" },
  { id: "react", name: "React 19", category: "frontend", description: "UI component library", color: "accent" },
  { id: "typescript", name: "TypeScript 5", category: "frontend", description: "Type-safe JavaScript", color: "accent" },
  { id: "tailwind", name: "Tailwind CSS", category: "frontend", description: "Utility-first CSS framework", color: "accent" },
  { id: "framer", name: "Framer Motion", category: "frontend", description: "Production animation library", color: "accent" },

  // Infrastructure
  { id: "postgresql", name: "PostgreSQL 16", category: "infrastructure", description: "Primary relational database", color: "warning" },
  { id: "redis", name: "Redis", category: "infrastructure", description: "Caching and queue broker", color: "warning" },
  { id: "docker", name: "Docker", category: "infrastructure", description: "Container runtime", color: "warning" },
  { id: "alembic", name: "Alembic", category: "infrastructure", description: "Database migrations", color: "warning" },
];

export const TECH_CATEGORIES: TechCategory[] = ["backend", "ai", "frontend", "infrastructure"];
