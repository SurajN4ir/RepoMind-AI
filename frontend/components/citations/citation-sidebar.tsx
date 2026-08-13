"use client";

import { useMemo, type ReactNode } from "react";
import { BookOpen, FileText } from "lucide-react";

import { CitationGroup } from "@/components/citations/citation-group";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { citationId, type SourceCitation } from "@/types/citation";

interface CitationSidebarProps {
  citations: SourceCitation[];
  repositoryId?: string;
  title?: string;
  activeFilePath?: string;
  activeLine?: number;
  selectedCitationId?: string;
  header?: ReactNode;
  emptyState?: ReactNode;
  className?: string;
  onNavigate?: (citation: SourceCitation) => void;
  onOpenFile?: (citation: SourceCitation) => void;
}

export function CitationSidebar({
  citations,
  repositoryId,
  title = "Sources",
  activeFilePath,
  activeLine,
  selectedCitationId,
  header,
  emptyState,
  className,
  onNavigate,
  onOpenFile,
}: CitationSidebarProps) {
  const groups = useMemo(() => {
    const map = new Map<string, SourceCitation[]>();
    const seen = new Set<string>();

    for (const c of citations) {
      const key = citationId(c);
      if (seen.has(key)) continue;
      seen.add(key);
      const existing = map.get(c.filePath) ?? [];
      existing.push(c);
      map.set(c.filePath, existing);
    }

    return Array.from(map.entries()).map(([filePath, items]) => ({
      filePath,
      citations: items,
    }));
  }, [citations]);

  return (
    <div
      className={cn(
        "flex flex-col overflow-hidden rounded-xl border border-border/50 bg-card",
        className,
      )}
    >
      {header ?? (
        <div className="flex items-center justify-between border-b border-border/50 px-4 py-3">
          <div className="flex items-center gap-2">
            <BookOpen size={14} className="text-muted-foreground" />
            <h3 className="text-sm font-semibold text-foreground">{title}</h3>
          </div>
          {citations.length > 0 && (
            <span className="text-xs text-muted-foreground">
              {citations.length} source{citations.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
      )}

      {groups.length > 0 ? (
        <ScrollArea className="flex-1 p-3">
          <div className="space-y-2">
            {groups.map((group) => (
              <CitationGroup
                key={group.filePath}
                filePath={group.filePath}
                citations={group.citations}
                repositoryId={repositoryId}
                activeFilePath={activeFilePath}
                activeLine={activeLine}
                selectedCitationId={selectedCitationId}
                onNavigate={onNavigate}
                onOpenFile={onOpenFile}
              />
            ))}
          </div>
        </ScrollArea>
      ) : (
        emptyState ?? (
          <div className="flex flex-1 flex-col items-center justify-center gap-2 p-6 text-center">
            <FileText size={24} className="text-muted-foreground/40" />
            <p className="text-xs text-muted-foreground/60">No sources yet</p>
          </div>
        )
      )}
    </div>
  );
}
