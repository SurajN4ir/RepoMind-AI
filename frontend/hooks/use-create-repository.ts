"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/services/api-client";
import { QUERY_KEYS } from "@/lib/constants";
import type { Repository } from "@/stores/workspace-store";

export interface CreateRepositoryRequest {
  name: string;
  url: string;
  provider: string;
  default_branch: string;
  description?: string;
}

export function useCreateRepository() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateRepositoryRequest) =>
      apiClient.post<Repository>("/api/repositories", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.repositories });
    },
  });
}
