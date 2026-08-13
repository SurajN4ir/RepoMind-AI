/**
 * features/landing/constants/landing.ts
 *
 * Centralised string constants, navigation links, and configuration
 * for the landing page. Keeping copy here makes localisation trivial.
 */

// ---------------------------------------------------------------------------
// Site-level
// ---------------------------------------------------------------------------

export const SITE_NAME = "RepoMind";
export const SITE_TAGLINE = "Repository Intelligence, Grounded in Your Codebase.";
export const SITE_DESCRIPTION =
  "RepoMind ingests, parses, and indexes your source code, then answers your questions with cited, accurate responses — no hallucinations.";

// ---------------------------------------------------------------------------
// Hero section
// ---------------------------------------------------------------------------

export const HERO_HEADLINE_WORDS = ["Understand", "Any", "Repository", "In Minutes."];

export const HERO_SUBHEADLINE =
  "RepoMind parses your source code at the AST level, builds a semantic index, and answers your questions with direct citations — no hallucinations, no guessing.";

export const HERO_CTA_PRIMARY = "Explore the Platform";
export const HERO_CTA_SECONDARY = "View on GitHub";

// ---------------------------------------------------------------------------
// Navigation links
// ---------------------------------------------------------------------------

export interface NavLink {
  label: string;
  href: string;
}

export const NAV_LINKS: NavLink[] = [
  { label: "Features", href: "#features" },
  { label: "Pipeline", href: "#pipeline" },
  { label: "Architecture", href: "#architecture" },
  { label: "Why RepoMind", href: "#why" },
  { label: "Tech Stack", href: "#tech" },
];

// ---------------------------------------------------------------------------
// Section labels
// ---------------------------------------------------------------------------

export const SECTION_LABELS = {
  pipeline: "Intelligence Pipeline",
  pipelineSubtitle:
    "From raw source code to grounded AI answers — every step is observable and replaceable.",
  features: "Features",
  featuresSubtitle:
    "Built for engineers who need answers, not approximations.",
  architecture: "Architecture",
  architectureSubtitle:
    "Clean, layered architecture with fully replaceable providers at every boundary.",
  why: "Why RepoMind",
  whySubtitle:
    "Traditional RAG breaks on code. RepoMind was built specifically for repositories.",
  tech: "Technology Stack",
  techSubtitle: "Production-grade open source technologies, thoughtfully composed.",
  demo: "See It In Action",
  demoSubtitle:
    "No backend. No sign-up. Just ask a question and watch RepoMind work.",
  cta: "Ready to understand your codebase?",
  ctaSubtitle: "Start querying in minutes. No configuration required.",
  ctaPrimary: "Get Started",
  ctaSecondary: "View on GitHub",
} as const;

// ---------------------------------------------------------------------------
// Footer
// ---------------------------------------------------------------------------

export interface FooterLinkGroup {
  label: string;
  links: { label: string; href: string }[];
}

export const FOOTER_GROUPS: FooterLinkGroup[] = [
  {
    label: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "Pipeline", href: "#pipeline" },
      { label: "Architecture", href: "#architecture" },
      { label: "Roadmap", href: "/roadmap" },
    ],
  },
  {
    label: "Documentation",
    links: [
      { label: "Getting Started", href: "/docs" },
      { label: "API Reference", href: "/docs/api" },
      { label: "Configuration", href: "/docs/config" },
      { label: "Deployment", href: "/docs/deployment" },
    ],
  },
  {
    label: "Community",
    links: [
      { label: "GitHub", href: "https://github.com" },
      { label: "Discussions", href: "/discussions" },
      { label: "Contributing", href: "/docs/contributing" },
      { label: "Changelog", href: "/changelog" },
    ],
  },
];

export const FOOTER_COPYRIGHT = `© ${new Date().getFullYear()} RepoMind. Built with care for engineers.`;
