"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight, FileText } from "lucide-react";

import { cn } from "@/lib/utils";
import { CitationItem } from "@/components/citations/citation-item";
import { citationId, type SourceCitation } from "@/types/citation";

interface CitationGroupProps {
  filePath: string;
  citations: SourceCitation[];
  repositoryId?: string;
  activeFilePath?: string;
  activeLine?: number;
  selectedCitationId?: string;
  onNavigate?: (citation: SourceCitation) => void;
  onOpenFile?: (citation: SourceCitation) => void;
}

export function CitationGroup({
  filePath,
  citations,
  repositoryId,
  activeFilePath,
  activeLine,
  selectedCitationId,
  onNavigate,
  onOpenFile,
}: CitationGroupProps) {
  const [expanded, setExpanded] = useState(true);

  const uniqueCitations = useMemo(() => {
    const seen = new Set<string>();
    return citations.filter((c) => {
      const key = citationId(c);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [citations]);

  const fileName = filePath.split("/").pop() ?? filePath;
  const isActive = activeFilePath === filePath;

  return (
    <div
      className={cn(
        "rounded-lg border border-border/50",
        isActive && "border-primary/30",
      )}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-medium text-foreground transition-colors hover:bg-muted/30"
      >
        {expanded ? (
          <ChevronDown size={12} className="flex-shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight size={12} className="flex-shrink-0 text-muted-foreground" />
        )}
        <FileText size={12} className="flex-shrink-0 text-muted-foreground" />
        <span className="truncate">{fileName}</span>
        <span className="flex-shrink-0 text-muted-foreground">
          ({uniqueCitations.length})
        </span>
      </button>
      {expanded && (
        <div className="border-t border-border/50 px-2 py-1">
          {uniqueCitations.map((c) => {
            const cid = citationId(c);
            return (
              <CitationItem
                key={cid}
                citation={c}
                repositoryId={repositoryId}
                isActive={
                  selectedCitationId !== undefined
                    ? selectedCitationId === cid
                    : activeFilePath === c.filePath && activeLine === c.lineStart
                }
                onNavigate={onNavigate}
                onOpenFile={onOpenFile}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
