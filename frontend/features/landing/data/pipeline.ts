/**
 * features/landing/data/pipeline.ts
 *
 * Data definition for the Repository Intelligence Pipeline.
 *
 * Changing nodes, labels, or visual properties here automatically
 * propagates to the animated pipeline section.
 */

import type { PipelineIconName } from "@/components/icons/pipeline-icons";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type PipelinePhase = "ingest" | "process" | "store" | "query" | "respond";

export interface PipelineNode {
  /** Unique identifier — used as animation target class suffix */
  id: string;
  /** Display label */
  label: string;
  /** Short description shown on hover / mobile tooltip */
  description: string;
  /** Icon identifier resolved by PipelineIcon */
  icon: PipelineIconName;
  /** Processing phase — drives color grouping */
  phase: PipelinePhase;
}

// ---------------------------------------------------------------------------
// Phase color map (maps to Tailwind / CSS token names)
// ---------------------------------------------------------------------------

export const PHASE_COLORS: Record<PipelinePhase, string> = {
  ingest: "primary",
  process: "accent",
  store: "success",
  query: "warning",
  respond: "primary",
};

export const PHASE_BG: Record<PipelinePhase, string> = {
  ingest: "bg-primary/10 border-primary/20",
  process: "bg-accent/10 border-accent/20",
  store: "bg-success/10 border-success/20",
  query: "bg-warning/10 border-warning/20",
  respond: "bg-primary/10 border-primary/20",
};

export const PHASE_ICON_COLOR: Record<PipelinePhase, string> = {
  ingest: "text-primary",
  process: "text-accent",
  store: "text-success",
  query: "text-warning",
  respond: "text-primary",
};

// ---------------------------------------------------------------------------
// Pipeline definition
// ---------------------------------------------------------------------------

export const PIPELINE_NODES: PipelineNode[] = [
  {
    id: "repository",
    label: "Repository",
    description: "Source code hosted on GitHub, GitLab, or Bitbucket",
    icon: "GitRepo",
    phase: "ingest",
  },
  {
    id: "clone",
    label: "Clone",
    description: "Clones the repository into an isolated workspace",
    icon: "Clone",
    phase: "ingest",
  },
  {
    id: "parse",
    label: "Parse",
    description: "Tree-sitter parses source files into AST structures",
    icon: "Parse",
    phase: "process",
  },
  {
    id: "chunk",
    label: "Chunk",
    description: "Semantic chunker splits code into meaningful, overlapping segments",
    icon: "Chunk",
    phase: "process",
  },
  {
    id: "embed",
    label: "Embed",
    description: "Embedding pipeline converts chunks into dense vector representations",
    icon: "Embed",
    phase: "process",
  },
  {
    id: "index",
    label: "Index",
    description: "Vectors are stored in pgvector / Qdrant for fast retrieval",
    icon: "Index",
    phase: "store",
  },
  {
    id: "retrieve",
    label: "Retrieve",
    description: "Query engine finds the most relevant chunks via semantic search",
    icon: "Retrieve",
    phase: "query",
  },
  {
    id: "ai",
    label: "AI",
    description: "AI Orchestrator synthesises context into a grounded response",
    icon: "AI",
    phase: "respond",
  },
];

// Convenience — ordered list of IDs for animation targeting
export const PIPELINE_IDS = PIPELINE_NODES.map((n) => n.id);
