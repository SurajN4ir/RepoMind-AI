import type { Metadata } from "next";

import { LandingPage } from "@/features/landing";

// ---------------------------------------------------------------------------
// Page-level metadata (overrides root layout defaults)
// ---------------------------------------------------------------------------

export const metadata: Metadata = {
  title: "RepoMind — Repository Intelligence Platform",
  description:
    "RepoMind parses your source code at the AST level, builds a semantic index, and answers your questions with direct citations — no hallucinations, no guessing.",
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function HomePage() {
  return <LandingPage />;
}
