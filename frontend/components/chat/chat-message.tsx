"use client";

import { useState } from "react";
import { Sparkles, User, Copy, Check, RotateCw, FileText, ChevronRight } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";

import { cn } from "@/lib/utils";
import { useStreamingText } from "@/hooks/use-streaming-text";
import { ROUTES } from "@/lib/constants";
import { MarkdownMessage } from "@/components/chat/markdown-message";
import type { SourceCitation } from "@/types/citation";

interface ChatMessageProps {
  sender: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
  isLatest?: boolean;
  repositoryId?: string;
  onRegenerate?: () => void;
  onShowAllSources?: () => void;
}

function SourceChip({ filePath, lineStart, repositoryId }: SourceCitation & { repositoryId?: string }) {
  const href = repositoryId
    ? `${ROUTES.dashboard}/${repositoryId}/files?file=${encodeURIComponent(filePath)}&line=${lineStart}`
    : "#";

  return (
    <Link
      href={href}
      className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-[10px] text-muted-foreground transition-colors hover:bg-muted/80 hover:text-foreground"
    >
      <FileText size={10} />
      <span className="max-w-[120px] truncate">{filePath}</span>
      <span className="text-[9px]">L{lineStart}</span>
    </Link>
  );
}

export function ChatMessage({
  sender,
  content,
  sources,
  isLatest,
  repositoryId,
  onRegenerate,
  onShowAllSources,
}: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isAssistant = sender === "assistant";
  const shouldStream = isAssistant && isLatest;
  const streamedContent = useStreamingText(shouldStream ? content : "");
  const displayText = shouldStream ? streamedContent : content;
  const isStreaming = shouldStream && streamedContent !== content;

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "group flex items-start gap-3 rounded-xl p-4",
        isAssistant ? "bg-muted/30" : "bg-primary/5",
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg",
          isAssistant
            ? "bg-primary/10 text-primary"
            : "bg-muted text-muted-foreground",
        )}
      >
        {isAssistant ? <Sparkles size={14} /> : <User size={14} />}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 text-sm leading-relaxed text-foreground">
            {isAssistant ? (
              <MarkdownMessage content={displayText} />
            ) : (
              displayText
            )}
            {isStreaming && (
              <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-primary" />
            )}
          </div>

          {isAssistant && !isStreaming && (
            <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
              <button
                onClick={handleCopy}
                className="flex h-7 w-7 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                aria-label="Copy message"
              >
                {copied ? <Check size={13} /> : <Copy size={13} />}
              </button>
              {onRegenerate && isLatest && (
                <button
                  onClick={onRegenerate}
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                  aria-label="Regenerate response"
                >
                  <RotateCw size={13} />
                </button>
              )}
            </div>
          )}
        </div>

        {isAssistant && sources && sources.length > 0 && (
          <div className="mt-2 flex flex-wrap items-center gap-1">
            {sources.slice(0, 3).map((src, i) => (
              <SourceChip key={i} {...src} repositoryId={repositoryId} />
            ))}
            {sources.length > 3 && (
              <button
                onClick={onShowAllSources}
                className="inline-flex items-center gap-0.5 rounded-full bg-muted/60 px-2 py-0.5 text-[10px] text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                +{sources.length - 3} more
                <ChevronRight size={10} />
              </button>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
