export const APP_TITLE = "RepoMind";

export const ROUTES = {
  home: "/",
  signIn: "/sign-in",
  signUp: "/sign-up",
  dashboard: "/repositories",
  search: "/search",
  settings: "/settings",
} as const;

export const API = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  endpoints: {
    health: "/api/health",
    repositories: "/api/repositories",
    search: "/api/search",
    query: "/api/query",
  },
} as const;

export const QUERY_KEYS = {
  repositories: ["repositories"] as const,
  repository: (id: string) => ["repositories", id] as const,
  search: (q: string) => ["search", q] as const,
  health: ["health"] as const,
} as const;

export const STORAGE_KEYS = {
  sidebarCollapsed: "repomind-sidebar-collapsed",
} as const;

export const NAV = {
  sidebarWidth: 280,
  sidebarCollapsedWidth: 64,
  topbarHeight: 56,
} as const;
