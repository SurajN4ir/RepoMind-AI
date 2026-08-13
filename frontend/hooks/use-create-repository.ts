"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/services/api-client";
import { QUERY_KEYS } from "@/lib/constants";

export interface CreateRepositoryRequest {
  name: string;
  url: string;
  provider: string;
  default_branch: string;
  description?: string;
}

export interface RepositoryResponse {
  id: string;
  name: string;
  url: string;
  provider: string;
  default_branch: string;
  description: string | null;
  status: string;
  language_summary: Record<string, number> | null;
  last_indexed_at: string | null;
  created_at: string;
  updated_at: string;
  total_files: number | null;
  indexed_file_count: number;
}

export function useCreateRepository() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateRepositoryRequest) =>
      apiClient.post<RepositoryResponse>("/api/repositories", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.repositories });
    },
  });
}
