import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";

export interface AnalyticsData {
  indexedRepositories: number;
  totalChunks: number;
  queriesAnswered: number;
  avgQueryLatencyMs: number | null;
  uptime: string | null;
  languagesSupported: number;
}

export function useAnalytics() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: () => apiClient.get<AnalyticsData>("/api/analytics"),
    retry: false,
    staleTime: 30_000,
  });
}
