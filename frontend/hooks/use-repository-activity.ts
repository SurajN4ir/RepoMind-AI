import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";

export interface ActivityEvent {
  id: string;
  event_type: string;
  message: string;
  timestamp: string;
}

export function useRepositoryActivity(repositoryId: string | null) {
  return useQuery({
    queryKey: ["activity", repositoryId],
    queryFn: () =>
      apiClient.get<ActivityEvent[]>(
        `/api/repositories/${repositoryId}/activity`,
      ),
    enabled: !!repositoryId,
    staleTime: 10_000,
    refetchInterval: 30_000,
  });
}
