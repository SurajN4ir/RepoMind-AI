/**
 * components/icons/pipeline-icons.tsx
 *
 * Icon components for the Repository Intelligence Pipeline.
 *
 * Each icon is a thin wrapper around a Lucide icon, exported with a
 * semantic name so the pipeline data layer can reference icon identifiers
 * without importing from Lucide directly.
 *
 * If the icon library changes, only this file needs updating.
 */

import {
  BrainCircuit,
  Code2,
  Database,
  Download,
  GitFork,
  Layers,
  Search,
  Sparkles,
  Zap,
} from "lucide-react";
import type { LucideProps } from "lucide-react";

export type PipelineIconName =
  | "GitRepo"
  | "Clone"
  | "Parse"
  | "Chunk"
  | "Embed"
  | "Index"
  | "Retrieve"
  | "AI"
  | "Zap";

const iconMap: Record<PipelineIconName, React.ComponentType<LucideProps>> = {
  GitRepo: GitFork,
  Clone: Download,
  Parse: Code2,
  Chunk: Layers,
  Embed: BrainCircuit,
  Index: Database,
  Retrieve: Search,
  AI: Sparkles,
  Zap: Zap,
};

interface PipelineIconProps extends LucideProps {
  name: PipelineIconName;
}

export function PipelineIcon({ name, ...props }: PipelineIconProps) {
  const Icon = iconMap[name];
  return <Icon {...props} />;
}

// Named re-exports for direct use
export {
  GitFork as GitRepoIcon,
  Download as CloneIcon,
  Code2 as ParseIcon,
  Layers as ChunkIcon,
  BrainCircuit as EmbedIcon,
  Database as IndexIcon,
  Search as RetrieveIcon,
  Sparkles as AIIcon,
};
