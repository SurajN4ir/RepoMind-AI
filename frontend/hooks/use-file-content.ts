"use client";

import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";

export interface FileContentResponse {
  path: string;
  content: string;
}

export function useFileContent(
  repositoryId: string | null,
  filePath: string | null,
) {
  return useQuery({
    queryKey: ["file-content", repositoryId, filePath],
    queryFn: () =>
      apiClient.get<FileContentResponse>(
        `/api/repositories/${repositoryId}/files/content`,
        { file_path: filePath! },
      ),
    enabled: !!repositoryId && !!filePath,
    retry: false,
    staleTime: 60_000,
  });
}
