import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";
import { QUERY_KEYS } from "@/lib/constants";

export interface SearchResult {
  id: string;
  repositoryId: string;
  repositoryName: string;
  filePath: string;
  lineStart: number;
  lineEnd: number;
  content: string;
  score: number;
}

export interface SearchQuery {
  repositoryId?: string;
  q: string;
  limit?: number;
}

function searchKey(params: SearchQuery): readonly string[] {
  return params.repositoryId
    ? [...QUERY_KEYS.search(params.q), params.repositoryId]
    : QUERY_KEYS.search(params.q);
}

export function useSearch(params: SearchQuery | null) {
  return useQuery({
    queryKey: params ? searchKey(params) : ["search", ""],
    queryFn: () =>
      apiClient.get<SearchResult[]>("/api/search", {
        q: params!.q,
        repository_id: params!.repositoryId,
        limit: String(params!.limit ?? 10),
      }),
    enabled: !!params && params.q.length > 0,
  });
}
