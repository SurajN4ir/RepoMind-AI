"use client";

import { FileCode, ChevronRight } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { ROUTES } from "@/lib/constants";
import type { SearchResult } from "@/hooks/use-search";

interface Props {
  result: SearchResult;
  showRepository?: boolean;
}

const scoreColor = (score: number) => {
  if (score >= 0.8) return "bg-success";
  if (score >= 0.5) return "bg-warning";
  return "bg-destructive";
};

export function SearchResultCard({ result, showRepository }: Props) {
  const href = `${ROUTES.dashboard}/${result.repositoryId}/files?file=${encodeURIComponent(result.filePath)}&line=${result.lineStart}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Link href={href}>
        <Card className="group cursor-pointer p-4 transition-colors hover:bg-surface/80">
          <div className="flex items-start justify-between gap-3">
            <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2 text-xs text-muted-foreground">
              {showRepository && (
                <span className="rounded bg-primary/10 px-1.5 py-0.5 font-medium text-primary">
                  {result.repositoryName}
                </span>
              )}
              <FileCode size={12} className="flex-shrink-0 text-primary" />
              <code className="truncate rounded bg-muted px-1.5 py-0.5 font-mono text-[11px]">
                {result.filePath}
              </code>
              <span className="flex-shrink-0">
                L{result.lineStart}–{result.lineEnd}
              </span>
            </div>
          </div>

          <div className="mt-2 flex items-center gap-3">
            <div className="flex h-2 flex-1 overflow-hidden rounded-full bg-muted">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${result.score * 100}%` }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className={cn("h-full rounded-full", scoreColor(result.score))}
              />
            </div>
            <span
              className={cn(
                "flex-shrink-0 text-[10px] font-medium",
                result.score >= 0.8 && "text-success",
                result.score >= 0.5 && result.score < 0.8 && "text-warning",
                result.score < 0.5 && "text-destructive",
              )}
            >
              {(result.score * 100).toFixed(0)}%
            </span>
          </div>

          <div className="mt-2 overflow-hidden rounded-lg border border-border bg-muted/50">
            <div className="flex items-center justify-between border-b border-border/50 px-3 py-1.5">
              <span className="text-[10px] text-muted-foreground">
                {result.filePath.split(".").pop()?.toUpperCase() ?? "CODE"}
              </span>
              <span className="text-[10px] text-muted-foreground">
                L{result.lineStart} – L{result.lineEnd}
              </span>
            </div>
            <pre className="overflow-x-auto p-3 text-xs leading-relaxed">
              <code className="font-mono text-foreground">{result.content}</code>
            </pre>
          </div>

          <div className="mt-2 flex items-center gap-1 text-[10px] text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100">
            <ChevronRight size={10} />
            {showRepository ? "View in repository" : "View in file"}
          </div>
        </Card>
      </Link>
    </motion.div>
  );
}
