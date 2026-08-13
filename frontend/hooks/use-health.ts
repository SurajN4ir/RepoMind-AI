import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";
import { QUERY_KEYS } from "@/lib/constants";

export function useHealth() {
  return useQuery({
    queryKey: QUERY_KEYS.health,
    queryFn: () => apiClient.get<{ status: string }>("/api/health"),
    refetchInterval: 30_000,
  });
}
