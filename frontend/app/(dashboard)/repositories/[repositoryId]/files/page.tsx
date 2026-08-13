"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo, useState } from "react";
import { Folder, File, ChevronRight, ChevronDown, Search, ArrowLeft } from "lucide-react";

import { FileInspector } from "@/components/explorer/file-inspector";
import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CodeViewer } from "@/components/code/code-viewer";
import { useRepository } from "@/hooks/use-repositories";
import { useFileTree, type FileNode } from "@/hooks/use-file-tree";
import { useFileContent } from "@/hooks/use-file-content";
import { useGraphData } from "@/hooks/use-graph-data";
import { cn } from "@/lib/utils";

function FileTreeItem({
  node,
  depth = 0,
  selectedPath,
  onSelect,
}: {
  node: FileNode;
  depth?: number;
  selectedPath?: string;
  onSelect?: (path: string) => void;
}) {
  const [expanded, setExpanded] = useState(depth < 1);
  const isSelected = node.path === selectedPath;

  if (node.type === "file") {
    return (
      <button
        onClick={() => onSelect?.(node.path)}
        className={cn(
          "flex w-full items-center gap-2 rounded-lg px-3 py-1.5 text-left text-sm transition-colors hover:bg-muted/40",
          isSelected && "bg-primary/10 text-primary",
        )}
        style={{ paddingLeft: `${16 + depth * 20}px` }}
      >
        <File size={14} className="flex-shrink-0 text-muted-foreground" />
        <span className={cn(isSelected && "font-medium")}>{node.name}</span>
      </button>
    );
  }

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 rounded-lg px-3 py-1.5 text-left text-sm transition-colors hover:bg-muted/40"
        style={{ paddingLeft: `${16 + depth * 20}px` }}
      >
        {expanded ? (
          <ChevronDown size={14} className="flex-shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight size={14} className="flex-shrink-0 text-muted-foreground" />
        )}
        <Folder size={14} className="flex-shrink-0 text-primary" />
        <span className="font-medium text-foreground">{node.name}</span>
      </button>
      {expanded &&
        node.children?.map((child) => (
          <FileTreeItem
            key={child.path}
            node={child}
            depth={depth + 1}
            selectedPath={selectedPath}
            onSelect={onSelect}
          />
        ))}
    </div>
  );
}

export default function RepositoryFilesPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const repoId = params.repositoryId as string;
  const { data: repo } = useRepository(repoId);
  const { data: fileTree, isLoading } = useFileTree(repoId);
  const { data: graphData } = useGraphData(repoId);
  const [filter, setFilter] = useState("");
  const selectedFile = searchParams.get("file");
  const highlightLine = searchParams.get("line");

  const handleFileSelect = useCallback(
    (path: string) => {
      router.push(
        `/repositories/${repoId}/files?file=${encodeURIComponent(path)}`,
        { scroll: false },
      );
    },
    [repoId, router],
  );

  const filterTree = useCallback(
    (nodes: FileNode[], query: string): FileNode[] => {
      if (!query) return nodes;
      return nodes
        .map((node) => {
          if (node.type === "file") {
            return node.name.toLowerCase().includes(query.toLowerCase())
              ? node
              : null;
          }
          const filteredChildren = node.children
            ? filterTree(node.children, query)
            : [];
          if (
            filteredChildren.length > 0 ||
            node.name.toLowerCase().includes(query.toLowerCase())
          ) {
            return { ...node, children: filteredChildren };
          }
          return null;
        })
        .filter(Boolean) as FileNode[];
    },
    [],
  );

  const { data: fileContent, isLoading: contentLoading } = useFileContent(
    repoId,
    selectedFile,
  );
  const filteredTree = useMemo(
    () => (fileTree ? filterTree(fileTree, filter) : []),
    [fileTree, filter, filterTree],
  );
  const fileLang = selectedFile?.split(".").pop() ?? "python";
  const fileLine = highlightLine ? parseInt(highlightLine, 10) : undefined;
  const highlightRange: [number, number] | undefined = fileLine
    ? [fileLine, fileLine + 4]
    : undefined;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={`Files — ${repo?.name ?? "Repository"}`}
        description="Browse repository file structure"
      />

      <div className={cn("grid gap-6", selectedFile ? "lg:grid-cols-7" : "lg:grid-cols-5")}>
        <div className="lg:col-span-2">
          <div className="relative mb-3">
            <Search size={14} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filter files..."
              className="focus-ring h-10 w-full rounded-xl border border-border bg-surface pl-9 pr-4 text-sm text-foreground placeholder:text-muted-foreground/60"
            />
          </div>

          <Card className="divide-y divide-border/50">
            <div className="flex items-center justify-between px-3 py-2 text-xs font-medium text-muted-foreground">
              <span>Repository files</span>
              {fileTree && <span>{fileTree.length} items</span>}
            </div>
            <div className="py-2">
              {isLoading ? (
                <div className="space-y-1 px-3 py-2">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="h-7 animate-pulse rounded bg-muted" />
                  ))}
                </div>
              ) : (
                filteredTree.map((node) => (
                  <FileTreeItem
                    key={node.path}
                    node={node}
                    selectedPath={selectedFile ?? undefined}
                    onSelect={handleFileSelect}
                  />
                ))
              )}
            </div>
          </Card>
        </div>

        <div className="lg:col-span-3">
          {selectedFile ? (
            <div>
              {searchParams.get("file") && (
                <div className="mb-3 flex items-center gap-2">
                  <Button
                    variant="ghost"
                    className="h-8 gap-1.5 text-xs"
                    onClick={() =>
                      router.push(`/repositories/${repoId}/files`, {
                        scroll: false,
                      })
                    }
                  >
                    <ArrowLeft size={12} />
                    Back to file tree
                  </Button>
                  {highlightLine && (
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
                      Referenced from chat
                    </span>
                  )}
                </div>
              )}
              {contentLoading ? (
                <CodeViewer
                  code=""
                  language={fileLang}
                  fileName={selectedFile}
                  isLoading
                />
              ) : fileContent ? (
                <CodeViewer
                  code={fileContent.content}
                  language={fileLang}
                  fileName={selectedFile}
                  highlightLines={highlightRange}
                />
              ) : (
                <Card className="flex h-full min-h-[300px] items-center justify-center p-6">
                  <div className="flex flex-col items-center gap-2 text-center">
                    <File size={32} className="text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      Could not load file content.
                    </p>
                  </div>
                </Card>
              )}
            </div>
          ) : (
            <Card className="flex h-full min-h-[300px] items-center justify-center p-6">
              <div className="flex flex-col items-center gap-2 text-center">
                <File size={32} className="text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Select a file from the tree to view its contents.
                </p>
              </div>
            </Card>
          )}
        </div>

        {selectedFile && (
          <div className="lg:col-span-2">
            <FileInspector
              repositoryId={repoId}
              filePath={selectedFile}
              graphData={graphData}
            />
          </div>
        )}
      </div>
    </div>
  );
}
