/**
 * features/landing/data/features.ts
 *
 * Feature card data for the "Features" landing section.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface FeatureCard {
  id: string;
  title: string;
  description: string;
  /** Icon name from feature-icons.tsx */
  icon: string;
  /** Badge label shown above the title */
  badge?: string;
  /** Highlight this card (primary/featured treatment) */
  featured?: boolean;
}

// ---------------------------------------------------------------------------
// Features
// ---------------------------------------------------------------------------

export const FEATURES: FeatureCard[] = [
  {
    id: "semantic-search",
    title: "Semantic Code Search",
    description:
      "Ask natural language questions and get back the exact functions, classes, and modules that are relevant — not just keyword matches.",
    icon: "SemanticSearchIcon",
    badge: "Core",
    featured: true,
  },
  {
    id: "ai-qa",
    title: "AI-Powered Q&A",
    description:
      "Ask 'How does authentication work?' and receive a grounded, cited answer with links to the source files — no hallucinations.",
    icon: "AIQAIcon",
    badge: "Core",
    featured: true,
  },
  {
    id: "code-chunking",
    title: "Semantic Chunking",
    description:
      "Tree-sitter-powered AST parsing ensures chunks align with real code boundaries: functions, classes, and modules — not arbitrary line counts.",
    icon: "CodeChunkingIcon",
    badge: "Engine",
  },
  {
    id: "smart-indexing",
    title: "Smart Indexing",
    description:
      "Dual vector stores (pgvector + Qdrant) give you flexibility between managed SQL and high-performance approximate nearest-neighbour search.",
    icon: "SmartIndexingIcon",
    badge: "Engine",
  },
  {
    id: "context-building",
    title: "Context Building",
    description:
      "The Context Builder assembles the right pieces of your codebase into a concise, token-efficient context window for the LLM.",
    icon: "ContextBuildingIcon",
    badge: "Intelligence",
  },
  {
    id: "multi-repo",
    title: "Multi-Repository",
    description:
      "Index multiple repositories and query across them simultaneously. Understand how services interact across your entire engineering org.",
    icon: "MultiRepoIcon",
    badge: "Scale",
  },
];

// ---------------------------------------------------------------------------
// Mock demo prompts
// ---------------------------------------------------------------------------

export const DEMO_PROMPTS: string[] = [
  "How does authentication work?",
  "Where is the embedding pipeline defined?",
  "What does the context builder do?",
  "How are repository chunks stored?",
];
