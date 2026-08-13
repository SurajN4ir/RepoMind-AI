import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";
import { QUERY_KEYS } from "@/lib/constants";
import type { Repository, RepositoryListResponse } from "@/stores/workspace-store";

export function useRepositories() {
  return useQuery({
    queryKey: QUERY_KEYS.repositories,
    queryFn: async () => {
      const response = await apiClient.get<RepositoryListResponse>("/api/repositories");
      return response.items;
    },
  });
}

export function useRepository(id: string | null) {
  return useQuery({
    queryKey: QUERY_KEYS.repository(id ?? ""),
    queryFn: () => apiClient.get<Repository>(`/api/repositories/${id}`),
    enabled: !!id,
  });
}

export function useDeleteRepository() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/repositories/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.repositories });
    },
  });
}
