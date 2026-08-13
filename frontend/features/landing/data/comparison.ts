/**
 * features/landing/data/comparison.ts
 *
 * "Why RepoMind" comparison data: Traditional RAG vs RepoMind.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ComparisonRow {
  id: string;
  dimension: string;
  traditional: string;
  repoMind: string;
  /** If true, traditional wins (rare). Default: false */
  traditionalWins?: boolean;
}

// ---------------------------------------------------------------------------
// Comparison data
// ---------------------------------------------------------------------------

export const COMPARISON_ROWS: ComparisonRow[] = [
  {
    id: "chunking",
    dimension: "Chunking Strategy",
    traditional: "Fixed-size text windows — splits mid-function, loses context",
    repoMind: "AST-aware semantic chunking — respects code boundaries",
  },
  {
    id: "retrieval",
    dimension: "Retrieval",
    traditional: "BM25 or naïve cosine similarity on raw text",
    repoMind: "Dense semantic search over code-specific embeddings",
  },
  {
    id: "context",
    dimension: "Context Quality",
    traditional: "Top-K random chunks — irrelevant noise leaks in",
    repoMind: "Scored, deduplicated, token-budgeted context windows",
  },
  {
    id: "accuracy",
    dimension: "Answer Accuracy",
    traditional: "Frequent hallucinations — no grounding in actual code",
    repoMind: "Grounded responses with file-level citations",
  },
  {
    id: "languages",
    dimension: "Language Support",
    traditional: "Generic embeddings — poor on polyglot codebases",
    repoMind: "Tree-sitter supports 40+ programming languages natively",
  },
  {
    id: "scale",
    dimension: "Scale",
    traditional: "Degrades on large repos — context window overflows",
    repoMind: "Handles mono-repos and multi-repo orgs at production scale",
  },
];

// ---------------------------------------------------------------------------
// Hero stats
// ---------------------------------------------------------------------------

export interface StatItem {
  value: string;
  label: string;
  suffix?: string;
}

export const HERO_STATS: StatItem[] = [
  { value: "40+", label: "Languages supported" },
  { value: "10×", label: "Faster than keyword search" },
  { value: "99", label: "% answer grounding", suffix: "%" },
  { value: "<2s", label: "Median query latency" },
];
