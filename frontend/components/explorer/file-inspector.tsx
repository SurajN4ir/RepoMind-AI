"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FileText,
  Loader2,
  Sparkles,
  ArrowUp,
  ArrowDown,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { CitationSidebar } from "@/components/citations/citation-sidebar";
import { useChatStream } from "@/hooks/use-chat-stream";
import { cn } from "@/lib/utils";
import type { GraphData } from "@/hooks/use-graph-data";
import type { SourceCitation } from "@/types/citation";

interface QuickAction {
  id: string;
  label: string;
  description: string;
  requiresAi: boolean;
}

interface FileInspectorProps {
  repositoryId: string;
  filePath: string;
  graphData?: GraphData;
}

const QUICK_ACTIONS: QuickAction[] = [
  {
    id: "explain",
    label: "Explain this file",
    description: "What does this file do?",
    requiresAi: true,
  },
  {
    id: "related",
    label: "Show related files",
    description: "Find files related to this one",
    requiresAi: true,
  },
  {
    id: "usage",
    label: "Where this is used",
    description: "See where this file is imported",
    requiresAi: true,
  },
  {
    id: "architecture",
    label: "Architecture role",
    description: "Understand its role in the codebase",
    requiresAi: true,
  },
];

const ACTION_QUERIES: Record<string, (filePath: string) => string> = {
  explain: (f) => `Explain this file: ${f}`,
  related: (f) => `What files are related to ${f}?`,
  usage: (f) => `Where is ${f} used or imported?`,
  architecture: (f) => `What is the architectural role of ${f}?`,
};

const _responseCache = new Map<
  string,
  { text: string; sources: SourceCitation[] }
>();
const _CACHE_MAX = 50;

export function FileInspector({
  repositoryId,
  filePath,
  graphData,
}: FileInspectorProps) {
  const router = useRouter();
  const { stream, cancel, isStreaming } = useChatStream();
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [responseText, setResponseText] = useState("");
  const [responseSources, setResponseSources] = useState<SourceCitation[]>([]);

  const incomingEdges =
    graphData?.edges.filter((e) => e.target === filePath) ?? [];
  const outgoingEdges =
    graphData?.edges.filter((e) => e.source === filePath) ?? [];

  useEffect(() => {
    cancel();
    setActiveAction(null);
    setResponseText("");
    setResponseSources([]);
  }, [filePath, cancel]);

  const handleAction = useCallback(
    (actionId: string) => {
      cancel();

      const cacheKey = `${filePath}:${actionId}`;
      const cached = _responseCache.get(cacheKey);
      if (cached) {
        setActiveAction(actionId);
        setResponseText(cached.text);
        setResponseSources(cached.sources);
        return;
      }

      setActiveAction(actionId);
      setResponseText("");
      setResponseSources([]);

      const sources: SourceCitation[] = [];

      stream(
        {
          repositoryId,
          query:
            ACTION_QUERIES[actionId]?.(filePath) ??
            `Explain this file: ${filePath}`,
        },
        {
          onToken: (token) => setResponseText((prev) => prev + token),
          onSources: (newSources) => {
            sources.push(...newSources);
            setResponseSources([...sources]);
          },
          onComplete: (text) => {
            _responseCache.set(cacheKey, { text, sources: [...sources] });
            if (_responseCache.size > _CACHE_MAX) {
              const firstKey = _responseCache.keys().next().value;
              if (firstKey) _responseCache.delete(firstKey);
            }
          },
          onError: () => {},
        },
      );
    },
    [filePath, repositoryId, stream, cancel],
  );

  const ext = filePath.split(".").pop() ?? "";
  const hasDeps = incomingEdges.length > 0 || outgoingEdges.length > 0;

  return (
    <Card className="flex h-full flex-col overflow-hidden">
      <div className="flex items-start justify-between border-b border-border/50 px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <FileText
              size={14}
              className="flex-shrink-0 text-muted-foreground"
            />
            <h3 className="truncate text-sm font-semibold text-foreground">
              Inspector
            </h3>
          </div>
          <p className="mt-0.5 truncate text-xs text-muted-foreground">
            {filePath}
          </p>
        </div>
        <Badge className="flex-shrink-0">{ext}</Badge>
      </div>

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
        {graphData && hasDeps && (
          <section>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Dependencies
            </h4>

            {incomingEdges.length > 0 && (
              <div className="mb-2">
                <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <ArrowDown size={12} />
                  <span>Inbound ({incomingEdges.length})</span>
                </div>
                <ul className="space-y-0.5">
                  {incomingEdges.map((edge) => (
                    <li key={edge.source}>
                      <Link
                        href={`/repositories/${repositoryId}/files?file=${encodeURIComponent(edge.source)}`}
                        scroll={false}
                        className="block truncate rounded px-2 py-1 text-xs text-foreground/80 transition-colors hover:bg-primary/10 hover:text-primary"
                      >
                        {edge.source}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {outgoingEdges.length > 0 && (
              <div>
                <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                  <ArrowUp size={12} />
                  <span>Outbound ({outgoingEdges.length})</span>
                </div>
                <ul className="space-y-0.5">
                  {outgoingEdges.map((edge) => (
                    <li key={edge.target}>
                      <Link
                        href={`/repositories/${repositoryId}/files?file=${encodeURIComponent(edge.target)}`}
                        scroll={false}
                        className="block truncate rounded px-2 py-1 text-xs text-foreground/80 transition-colors hover:bg-primary/10 hover:text-primary"
                      >
                        {edge.target}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {!graphData && (
          <section>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Dependencies
            </h4>
            <div className="space-y-1">
              {Array.from({ length: 3 }).map((_, i) => (
                <div
                  key={i}
                  className="h-3 animate-pulse rounded bg-muted"
                />
              ))}
            </div>
          </section>
        )}

        <section>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Quick Actions
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.id}
                onClick={() => handleAction(action.id)}
                disabled={isStreaming && activeAction === action.id}
                className={cn(
                  "flex items-center gap-2 rounded-lg border border-border/50 px-3 py-2 text-left text-xs transition-all hover:border-primary/30 hover:bg-primary/5",
                  activeAction === action.id &&
                    isStreaming &&
                    "border-primary/30 bg-primary/5",
                )}
              >
                <Sparkles
                  size={12}
                  className={cn(
                    "flex-shrink-0 text-muted-foreground",
                    activeAction === action.id && "text-primary",
                  )}
                />
                <div className="min-w-0 flex-1">
                  <span className="block truncate font-medium text-foreground">
                    {action.label}
                  </span>
                  <span className="block truncate text-muted-foreground">
                    {action.description}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </section>

        {activeAction && (
          <section>
            <h4 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {isStreaming && (
                <span className="flex items-center gap-1">
                  <Loader2 size={12} className="animate-spin" />
                  Streaming...
                </span>
              )}
              {!isStreaming && responseText && "Response"}
            </h4>

            {responseText ? (
              <div className="rounded-lg border border-border/50 bg-muted/10 p-3">
                <p className="whitespace-pre-wrap text-xs leading-relaxed text-foreground/90">
                  {responseText}
                </p>
                {responseSources.length > 0 && (
                  <div className="mt-3">
                    <CitationSidebar
                      citations={responseSources}
                      repositoryId={repositoryId}
                      title="Sources in this response"
                      onOpenFile={(citation) => {
                        const url = `/repositories/${repositoryId}/files?file=${encodeURIComponent(citation.filePath)}${citation.lineStart > 0 ? `&line=${citation.lineStart}` : ""}`;
                        router.push(url, { scroll: false });
                      }}
                    />
                  </div>
                )}
              </div>
            ) : isStreaming ? (
              <div className="flex items-center gap-2 rounded-lg border border-border/50 p-3">
                <Loader2
                  size={14}
                  className="animate-spin text-muted-foreground"
                />
                <span className="text-xs text-muted-foreground">
                  Generating response...
                </span>
              </div>
            ) : null}
          </section>
        )}
      </div>
    </Card>
  );
}
