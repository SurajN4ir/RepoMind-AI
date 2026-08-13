import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/services/api-client";

export interface FileNode {
  name: string;
  type: "file" | "directory";
  path: string;
  children?: FileNode[];
}

interface FileTreeResponse {
  items: FileNode[];
}

export function useFileTree(repositoryId: string | null) {
  return useQuery({
    queryKey: ["file-tree", repositoryId],
    queryFn: async () => {
      const resp = await apiClient.get<FileTreeResponse>(
        `/api/repositories/${repositoryId}/files`,
      );
      return resp.items;
    },
    enabled: !!repositoryId,
    retry: false,
    staleTime: 60_000,
  });
}
