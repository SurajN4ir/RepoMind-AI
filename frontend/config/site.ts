export const siteConfig = {
  name: "RepoMind",
  tagline: "Repository Intelligence Platform",
  description:
    "RepoMind parses your source code at the AST level, builds a semantic index, and answers your questions with direct citations — no hallucinations, no guessing.",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  ogImage: "/og.png",
  author: "RepoMind Team",
  keywords: [
    "repository intelligence",
    "code search",
    "AI codebase",
    "semantic search",
    "code Q&A",
    "developer tools",
  ],
  links: {
    github: "https://github.com/anomalyco/repomind",
    twitter: "https://x.com/repomind",
    docs: "https://repomind.ai/docs",
  },
} as const;

export type SiteConfig = typeof siteConfig;
