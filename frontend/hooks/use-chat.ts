import { useRef } from "react";
import { useMutation } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  answer: string;
  sources?: { filePath: string; lineStart: number; lineEnd: number }[];
}

interface QueryResponse {
  repository_id: string;
  success: boolean;
  response_text: string | null;
  citations: { filePath: string; lineStart: number; lineEnd: number }[];
}

function useConversationId(): string {
  const ref = useRef<string | null>(null);
  if (!ref.current) {
    const stored = typeof window !== "undefined" ? sessionStorage.getItem("conversation_id") : null;
    ref.current = stored ?? crypto.randomUUID();
    if (typeof window !== "undefined" && !stored) {
      sessionStorage.setItem("conversation_id", ref.current);
    }
  }
  return ref.current;
}

export function useChatMutation() {
  const conversationId = useConversationId();
  return useMutation({
    mutationFn: async (params: { repositoryId: string; query: string }) => {
      const data = await apiClient.post<QueryResponse>(
        `/api/repositories/${params.repositoryId}/query`,
        {
          text: params.query,
          conversation_id: conversationId,
        },
      );
      return {
        answer: data.response_text ?? "",
        sources: data.citations,
      } as ChatResponse;
    },
  });
}
