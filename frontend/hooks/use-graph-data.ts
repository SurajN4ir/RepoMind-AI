import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";

export interface GraphNode {
  id: string;
  label: string;
  type: "file" | "directory" | "module";
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export function useGraphData(repositoryId: string | null) {
  return useQuery({
    queryKey: ["graph", repositoryId],
    queryFn: () =>
      apiClient.get<GraphData>(`/api/repositories/${repositoryId}/graph`),
    enabled: !!repositoryId,
    staleTime: 60_000,
  });
}
