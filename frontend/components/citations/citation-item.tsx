"use client";

import { useCallback } from "react";
import Link from "next/link";
import { ExternalLink } from "lucide-react";

import { cn } from "@/lib/utils";
import type { SourceCitation } from "@/types/citation";

interface CitationItemProps {
  citation: SourceCitation;
  repositoryId?: string;
  isActive?: boolean;
  onNavigate?: (citation: SourceCitation) => void;
  onOpenFile?: (citation: SourceCitation) => void;
}

export function CitationItem({
  citation,
  repositoryId,
  isActive,
  onNavigate,
  onOpenFile,
}: CitationItemProps) {
  const fileName = citation.filePath.split("/").pop() ?? citation.filePath;
  const hasLineRange = citation.lineStart > 0;

  const handleClick = useCallback(() => {
    onNavigate?.(citation);
  }, [onNavigate, citation]);

  const handleOpenFile = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      if (onOpenFile) {
        onOpenFile(citation);
      }
    },
    [onOpenFile, citation],
  );

  const openFileHref = repositoryId
    ? `/repositories/${repositoryId}/files?file=${encodeURIComponent(citation.filePath)}${citation.lineStart > 0 ? `&line=${citation.lineStart}` : ""}`
    : "#";

  const content = (
    <div
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleClick();
        }
      }}
      className={cn(
        "group flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-xs transition-colors hover:bg-muted/50",
        isActive && "bg-primary/10 text-primary",
      )}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "block truncate font-medium",
              isActive ? "text-primary" : "text-foreground",
            )}
          >
            {fileName}
          </span>
          {hasLineRange && (
            <span
              className={cn(
                "flex-shrink-0 rounded px-1.5 py-0.5 text-[10px]",
                isActive
                  ? "bg-primary/20 text-primary"
                  : "bg-muted text-muted-foreground",
              )}
            >
              L{citation.lineStart}{citation.lineEnd > citation.lineStart ? `-${citation.lineEnd}` : ""}
            </span>
          )}
        </div>
        <span className="mt-0.5 block truncate text-muted-foreground">
          {citation.filePath}
        </span>
        {citation.description && (
          <span className="mt-0.5 block truncate italic text-muted-foreground/60">
            {citation.description}
          </span>
        )}
      </div>

      {onOpenFile && (
        <button
          onClick={handleOpenFile}
          className="flex-shrink-0 rounded-lg p-1.5 text-muted-foreground opacity-0 transition-all hover:bg-background hover:text-foreground group-hover:opacity-100"
          title="Open file"
        >
          <ExternalLink size={12} />
        </button>
      )}
    </div>
  );

  if (!onNavigate && !onOpenFile && repositoryId) {
    return (
      <Link
        href={openFileHref}
        scroll={false}
        className={cn(
          "group flex items-center gap-2 rounded-lg px-3 py-2 text-xs transition-colors hover:bg-muted/50",
          isActive && "bg-primary/10 text-primary",
        )}
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "block truncate font-medium",
                isActive ? "text-primary" : "text-foreground",
              )}
            >
              {fileName}
            </span>
            {hasLineRange && (
              <span
                className={cn(
                  "flex-shrink-0 rounded px-1.5 py-0.5 text-[10px]",
                  isActive
                    ? "bg-primary/20 text-primary"
                    : "bg-muted text-muted-foreground",
                )}
              >
                L{citation.lineStart}{citation.lineEnd > citation.lineStart ? `-${citation.lineEnd}` : ""}
              </span>
            )}
          </div>
          <span className="mt-0.5 block truncate text-muted-foreground">
            {citation.filePath}
          </span>
          {citation.description && (
            <span className="mt-0.5 block truncate italic text-muted-foreground/60">
              {citation.description}
            </span>
          )}
        </div>

        <span className="flex-shrink-0 rounded-lg p-1.5 text-muted-foreground opacity-0 transition-all group-hover:opacity-100">
          <ExternalLink size={12} />
        </span>
      </Link>
    );
  }

  return content;
}
