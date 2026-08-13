"use client";

import { create } from "zustand";

export interface Repository {
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

export interface RepositoryListResponse {
  items: Repository[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

type WorkspaceState = {
  activeRepositoryId: string | null;
  setActiveRepository: (id: string | null) => void;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeRepositoryId: null,
  setActiveRepository: (id) => set({ activeRepositoryId: id }),
}));
