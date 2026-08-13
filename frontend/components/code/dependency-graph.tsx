"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
  type NodeProps,
  Handle,
  Position,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";
import { motion } from "motion/react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import {
  aggregateToModules,
  type GraphNode,
  type GraphEdge,
  type ModuleInfo,
} from "@/lib/graph-utils";

interface DependencyGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  isLoading?: boolean;
  repositoryId?: string;
  viewMode?: "file" | "module";
  onViewModeChange?: (mode: "file" | "module") => void;
}

const typeColors: Record<string, string> = {
  file: "border-blue-500/30 bg-blue-500/10 text-blue-500",
  directory: "border-amber-500/30 bg-amber-500/10 text-amber-500",
  module: "border-purple-500/30 bg-purple-500/10 text-purple-500",
};

const typeLabels: Record<string, string> = {
  file: "File",
  directory: "Dir",
  module: "Module",
};

function GraphNodeComponent({ data }: NodeProps) {
  const nodeType = (data.nodeType as string) ?? "file";
  return (
    <div
      className={cn(
        "rounded-lg border-2 px-3 py-2 text-xs font-mono shadow-sm backdrop-blur-sm",
        typeColors[nodeType] ?? "border-muted bg-muted text-muted-foreground",
      )}
    >
      <Handle type="target" position={Position.Top} className="!border-border !bg-muted-foreground/40" />
      <div className="flex items-center gap-2">
        <span className={cn("rounded px-1 py-0.5 text-[9px] font-medium uppercase", typeColors[nodeType])}>
          {typeLabels[nodeType]}
        </span>
        <span className="max-w-[140px] truncate">{data.label as string}</span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!border-border !bg-muted-foreground/40" />
    </div>
  );
}

const nodeTypes = { graphNode: GraphNodeComponent };

export function DependencyGraph({
  nodes,
  edges,
  isLoading,
  repositoryId,
  viewMode = "file",
  onViewModeChange,
}: DependencyGraphProps) {
  const router = useRouter();
  const [selectedModule, setSelectedModule] = useState<ModuleInfo | null>(null);

  const { nodes: moduleNodes, edges: moduleEdges, modules } = useMemo(
    () => aggregateToModules(nodes, edges),
    [nodes, edges],
  );

  const { rfNodes, rfEdges } = useMemo(() => {
    const isModuleView = viewMode === "module";
    const sourceNodes = isModuleView ? moduleNodes : nodes;
    const sourceEdges = isModuleView ? moduleEdges : edges;

    const g = new dagre.graphlib.Graph();
    g.setDefaultEdgeLabel(() => ({}));
    g.setGraph({ rankdir: "TB", nodesep: 60, ranksep: 80, marginx: 40, marginy: 40 });

    for (const node of sourceNodes) {
      g.setNode(node.id, { width: 160, height: 44 });
    }
    for (const edge of sourceEdges) {
      g.setEdge(edge.source, edge.target);
    }

    dagre.layout(g);

    const rfn: Node[] = sourceNodes.map((node) => {
      const dagreNode = g.node(node.id);
      return {
        id: node.id,
        type: "graphNode",
        position: { x: dagreNode.x - 80, y: dagreNode.y - 22 },
        data: { label: node.label, nodeType: node.type },
      };
    });

    const rfe: Edge[] = sourceEdges.map((edge, i) => ({
      id: `e-${i}`,
      source: edge.source,
      target: edge.target,
      type: "smoothstep",
      animated: true,
      markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 12 },
      style: { stroke: "hsl(var(--border))", strokeWidth: 1.5 },
    }));

    return { rfNodes: rfn, rfEdges: rfe };
  }, [nodes, edges, viewMode, moduleNodes, moduleEdges]);

  const handleNodeClick = (_event: unknown, node: Node) => {
    if (viewMode === "module") {
      const info = modules.get(node.id);
      if (info) {
        setSelectedModule(info);
        return;
      }
    }
    setSelectedModule(null);
    if (repositoryId) {
      router.push(
        `/repositories/${repositoryId}/files?file=${encodeURIComponent(node.id)}`,
      );
    }
  };

  const handleExpandModule = () => {
    setSelectedModule(null);
    onViewModeChange?.("file");
  };

  if (isLoading) {
    return (
      <Card className="p-5">
        <div className="mb-4 h-4 w-36 animate-pulse rounded bg-muted" />
        <div className="flex aspect-[8/5] items-center justify-center rounded-xl bg-muted/30">
          <div className="h-32 w-32 animate-pulse rounded-full bg-muted" />
        </div>
      </Card>
    );
  }

  if (nodes.length === 0) {
    return (
      <Card className="p-5">
        <h3 className="mb-4 text-sm font-semibold text-foreground">Dependency Graph</h3>
        <div className="flex aspect-[8/5] items-center justify-center rounded-xl bg-muted/30">
          <p className="text-sm text-muted-foreground">
            No dependency data available. Index a repository to generate its dependency graph.
          </p>
        </div>
      </Card>
    );
  }

  const displayNodeCount = viewMode === "module" ? moduleNodes.length : nodes.length;
  const displayEdgeCount = viewMode === "module" ? moduleEdges.length : edges.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="relative"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Dependency Graph</h3>

        <div className="flex items-center overflow-hidden rounded-lg border border-border bg-muted/30 p-0.5">
          <button
            onClick={() => {
              setSelectedModule(null);
              onViewModeChange?.("file");
            }}
            className={cn(
              "rounded-md px-3 py-1 text-xs font-medium transition-colors",
              viewMode === "file"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            File Graph
          </button>
          <button
            onClick={() => {
              setSelectedModule(null);
              onViewModeChange?.("module");
            }}
            className={cn(
              "rounded-md px-3 py-1 text-xs font-medium transition-colors",
              viewMode === "module"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            Module Graph
          </button>
        </div>
      </div>

      {selectedModule && (
        <div className="mb-3 flex items-center gap-3 rounded-lg border border-purple-500/30 bg-purple-500/5 px-4 py-2.5">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-foreground">{selectedModule.name}</span>
              <span className="rounded bg-purple-500/10 px-1.5 py-0.5 text-[10px] font-medium text-purple-500">Module</span>
            </div>
            <div className="mt-1 flex items-center gap-3 text-[11px] text-muted-foreground">
              <span>{selectedModule.fileCount} file{selectedModule.fileCount !== 1 ? "s" : ""}</span>
              <span>{selectedModule.inbound} inbound</span>
              <span>{selectedModule.outbound} outbound</span>
            </div>
          </div>
          <button
            onClick={handleExpandModule}
            className="rounded-lg bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-primary/20"
          >
            Expand to File Graph
          </button>
          <button
            onClick={() => setSelectedModule(null)}
            className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            title="Close"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M3 3L9 9M9 3L3 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-border" style={{ height: 500 }}>
        <ReactFlow
          key={`${viewMode}-${moduleNodes.length}`}
          nodes={rfNodes}
          edges={rfEdges}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
          proOptions={{ hideAttribution: true }}
          onNodeClick={handleNodeClick}
        >
          <Background gap={20} size={1} color="hsl(var(--border))" />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>

      <div className="mt-3 flex items-center gap-4 text-[10px] text-muted-foreground">
        {viewMode === "file" ? (
          <>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              Files
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              Directories
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-purple-500" />
              Modules
            </span>
          </>
        ) : (
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-purple-500" />
            Modules
          </span>
        )}
        <span className="ml-auto">
          {displayNodeCount} node{displayNodeCount !== 1 ? "s" : ""} · {displayEdgeCount} edge{displayEdgeCount !== 1 ? "s" : ""}
        </span>
      </div>
    </motion.div>
  );
}
