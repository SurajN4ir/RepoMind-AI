"use client";

import { useState, useRef, useCallback } from "react";

import { API } from "@/lib/constants";

interface StreamCallbacks {
  onToken: (token: string) => void;
  onSources?: (sources: { filePath: string; lineStart: number; lineEnd: number }[]) => void;
  onComplete?: (fullText: string) => void;
  onError?: (error: Error) => void;
}

function getConversationId(): string {
  if (typeof window === "undefined") return "";
  const stored = sessionStorage.getItem("conversation_id");
  if (stored) return stored;
  const id = crypto.randomUUID();
  sessionStorage.setItem("conversation_id", id);
  return id;
}

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const stream = useCallback(
    async (
      params: { repositoryId: string; query: string },
      callbacks: StreamCallbacks,
    ) => {
      abortRef.current = new AbortController();
      setIsStreaming(true);

      let fullText = "";

      try {
        const url = `${API.baseUrl}/api/repositories/${params.repositoryId}/query/stream`;
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: params.query,
            conversation_id: getConversationId(),
          }),
          signal: abortRef.current.signal,
        });

        if (response.status === 404) {
          throw new Error("streaming not supported");
        }
        if (!response.ok) {
          throw new Error(`Stream request failed: ${response.status}`);
        }

        const contentType = response.headers.get("content-type") ?? "";
        if (contentType.includes("text/event-stream") || response.body) {
          const reader = response.body!.getReader();
          const decoder = new TextDecoder();
          let buffer = "";

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() ?? "";

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const data = line.slice(6);
                if (data === "[DONE]") break;

                try {
                  const parsed = JSON.parse(data);
                  if (parsed.token) {
                    fullText += parsed.token;
                    callbacks.onToken(parsed.token);
                  }
                  if (parsed.sources) {
                    callbacks.onSources?.(parsed.sources);
                  }
                } catch {
                  fullText += data;
                  callbacks.onToken(data);
                }
              }
            }
          }
        } else {
          const data = await response.json();
          fullText = data.response_text ?? JSON.stringify(data);
          callbacks.onToken(fullText);
          if (data.citations) {
            callbacks.onSources?.(data.citations);
          }
        }

        callbacks.onComplete?.(fullText);
        return fullText;
      } catch (err) {
        if ((err as Error).name === "AbortError") return fullText;
        callbacks.onError?.(err as Error);
        throw err;
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [],
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsStreaming(false);
  }, []);

  return { stream, cancel, isStreaming };
}
