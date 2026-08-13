"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";
import { QUERY_KEYS } from "@/lib/constants";

export interface IndexingResponse {
  repository_id: string;
  success: boolean;
  elapsed_seconds: number;
  errors: string[];
  chunks_created: boolean;
  indexed: boolean;
}

export function useIndexRepository() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (repositoryId: string) =>
      apiClient.post<IndexingResponse>(`/api/repositories/${repositoryId}/index`),
    onSuccess: (data, repositoryId) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.repository(repositoryId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.repositories });
    },
    onError: (_error, repositoryId) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.repository(repositoryId) });
    },
  });
}
