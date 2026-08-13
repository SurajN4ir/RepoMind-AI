"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useState, useRef, useEffect, useCallback } from "react";
import { Bot, Sparkles, Square, PanelRight } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CitationSidebar } from "@/components/citations/citation-sidebar";
import { ChatMessage } from "@/components/chat/chat-message";
import { ChatInput } from "@/components/chat/chat-input";
import { useRepository } from "@/hooks/use-repositories";
import { useChatMutation, type ChatResponse } from "@/hooks/use-chat";
import { useChatStream } from "@/hooks/use-chat-stream";
import { cn } from "@/lib/utils";
import type { SourceCitation } from "@/types/citation";

interface Message {
  sender: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
}

export default function RepositoryChatPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const repoId = params.repositoryId as string;
  const { data: repo } = useRepository(repoId);
  const chatMutation = useChatMutation();
  const chatStream = useChatStream();
  const bottomRef = useRef<HTMLDivElement>(null);
  const sidebarRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentSources, setCurrentSources] = useState<SourceCitation[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const activeFilePath = searchParams.get("citationFile");
  const activeLine = searchParams.get("citationLine")
    ? parseInt(searchParams.get("citationLine")!, 10)
    : undefined;

  const showSidebar = sidebarOpen && (currentSources.length > 0 || messages.some((m) => (m.sources?.length ?? 0) > 0));

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent, isStreaming]);

  const scrollToSidebar = useCallback(() => {
    setSidebarOpen(true);
    setTimeout(() => {
      sidebarRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }, []);

  const handleNavigate = useCallback(
    (citation: SourceCitation) => {
      const newParams = new URLSearchParams(searchParams.toString());
      newParams.set("citationFile", citation.filePath);
      newParams.set("citationLine", String(citation.lineStart));
      router.replace(`/repositories/${repoId}/chat?${newParams.toString()}`, {
        scroll: false,
      });
    },
    [repoId, router, searchParams],
  );

  const handleOpenFile = useCallback(
    (citation: SourceCitation) => {
      const url = `/repositories/${repoId}/files?file=${encodeURIComponent(citation.filePath)}${citation.lineStart > 0 ? `&line=${citation.lineStart}` : ""}`;
      router.push(url, { scroll: false });
    },
    [repoId, router],
  );

  const fallbackToNonStreaming = useCallback(
    (query: string) => {
      chatMutation.mutate(
        { repositoryId: repoId, query },
        {
          onSuccess: (data: ChatResponse) => {
            const sources = (data.sources ?? []) as SourceCitation[];
            setCurrentSources(sources);
            setMessages((prev) => [
              ...prev,
              { sender: "assistant", content: data.answer, sources },
            ]);
          },
          onError: () => {
            setMessages((prev) => [
              ...prev,
              { sender: "assistant", content: "Sorry, I encountered an error processing your request." },
            ]);
          },
        },
      );
      setStreamingContent("");
      setIsStreaming(false);
    },
    [repoId, chatMutation],
  );

  const streamOrFallback = useCallback(
    (query: string) => {
      setIsStreaming(true);
      setStreamingContent("");
      setCurrentSources([]);

      let accumulatedSources: SourceCitation[] = [];

      chatStream
        .stream(
          { repositoryId: repoId, query },
          {
            onToken: (token) => {
              setStreamingContent((prev) => prev + token);
            },
            onSources: (sources) => {
              accumulatedSources = sources;
              setCurrentSources([...sources]);
            },
            onComplete: (fullText) => {
              setMessages((prev) => [
                ...prev,
                { sender: "assistant", content: fullText, sources: accumulatedSources },
              ]);
              setStreamingContent("");
              setIsStreaming(false);
            },
            onError: () => {
              fallbackToNonStreaming(query);
            },
          },
        )
        .catch(() => {});
    },
    [repoId, chatStream, fallbackToNonStreaming],
  );

  const handleSend = useCallback(
    (query: string) => {
      setMessages((prev) => [...prev, { sender: "user", content: query }]);
      streamOrFallback(query);
    },
    [streamOrFallback],
  );

  const handleRegenerate = useCallback(() => {
    setMessages((prev) => {
      const lastAssistantIdx = [...prev].reverse().findIndex((m) => m.sender === "assistant");
      if (lastAssistantIdx === -1) return prev;
      const assistantIdx = prev.length - 1 - lastAssistantIdx;
      const lastUser = [...prev.slice(0, assistantIdx)].reverse().find((m) => m.sender === "user");
      if (lastUser) {
        streamOrFallback(lastUser.content);
        return prev.slice(0, assistantIdx);
      }
      return prev;
    });
  }, [streamOrFallback]);

  const isPending = isStreaming || chatMutation.isPending;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={`Chat — ${repo?.name ?? "Repository"}`}
        description="Ask questions about this repository"
      />

      <div className={cn("grid gap-6", showSidebar ? "lg:grid-cols-4" : "lg:grid-cols-1")}>
        <div className={showSidebar ? "lg:col-span-3" : "lg:col-span-1"}>
          <Card className="flex flex-1 flex-col overflow-hidden" style={{ minHeight: "65vh" }}>
            <div className="flex-1 space-y-2 overflow-y-auto p-4">
              {messages.length === 0 && !isPending && (
                <div className="flex h-full flex-col items-center justify-center gap-3 py-16 text-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                    <Bot size={28} className="text-primary" />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Ask anything about this repository.
                  </p>
                  <p className="max-w-sm text-xs text-muted-foreground/60">
                    For example: &ldquo;How does authentication work?&rdquo; or &ldquo;Where are the API routes defined?&rdquo;
                  </p>
                </div>
              )}

              {messages.map((msg, i) => (
                <ChatMessage
                  key={i}
                  sender={msg.sender}
                  content={msg.content}
                  sources={msg.sources}
                  repositoryId={repoId}
                  isLatest={false}
                  onRegenerate={
                    i === messages.length - 1 && msg.sender === "assistant"
                      ? handleRegenerate
                      : undefined
                  }
                  onShowAllSources={scrollToSidebar}
                />
              ))}

              {isStreaming ? (
                <ChatMessage
                  sender="assistant"
                  content={streamingContent}
                  isLatest
                  repositoryId={repoId}
                  onShowAllSources={scrollToSidebar}
                />
              ) : chatMutation.isPending ? (
                <div className="flex items-start gap-3 rounded-xl bg-muted/30 p-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Sparkles size={14} />
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/40" />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/40" style={{ animationDelay: "0.1s" }} />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/40" style={{ animationDelay: "0.2s" }} />
                  </div>
                </div>
              ) : null}

              <div ref={bottomRef} />
            </div>

            {isStreaming && (
              <div className="flex justify-center border-t border-border px-4 py-2">
                <button
                  onClick={() => chatStream.cancel()}
                  className="inline-flex items-center gap-2 rounded-full bg-destructive/10 px-4 py-1.5 text-xs font-medium text-destructive transition-colors hover:bg-destructive/20"
                >
                  <Square size={12} fill="currentColor" />
                  Stop Generating
                </button>
              </div>
            )}

            <ChatInput
              onSend={handleSend}
              disabled={isPending}
              placeholder="Ask a question about this repository..."
            />
          </Card>
        </div>

        <div ref={sidebarRef} className={cn(showSidebar ? "lg:col-span-1" : "hidden")}>
          {showSidebar && (
            <CitationSidebar
              citations={
                isStreaming
                  ? currentSources
                  : (messages
                      .filter((m) => m.sender === "assistant")
                      .flatMap((m) => m.sources ?? [])
                  )
              }
              repositoryId={repoId}
              title="Sources"
              activeFilePath={activeFilePath ?? undefined}
              activeLine={activeLine}
              onNavigate={handleNavigate}
              onOpenFile={handleOpenFile}
            />
          )}
        </div>
      </div>

      {!showSidebar && messages.some((m) => (m.sources?.length ?? 0) > 0) && (
        <div className="flex justify-center">
          <Button
            variant="secondary"
            onClick={() => setSidebarOpen(true)}
            className="gap-2"
          >
            <PanelRight size={14} />
            Show Sources
          </Button>
        </div>
      )}
    </div>
  );
}
