"use client";

/**
 * features/landing/sections/mock-demo-section.tsx
 *
 * Interactive live mock demo — simulates the full RepoMind query lifecycle:
 *
 *   IDLE → TYPING → PLANNING → SEARCHING → BUILDING → ANSWERING → DONE
 *
 * No backend. All data is scripted via useMockDemo().
 *
 * Accessibility:
 * - aria-live="polite" on the result areas so screen readers announce updates
 * - role="status" on phase indicator
 * - All buttons have descriptive aria-labels
 * - Keyboard navigable (Tab + Enter/Space)
 */

import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import { useState } from "react";

import { TerminalIcon, SparklesIcon, FileSearchIcon } from "@/components/icons/feature-icons";
import { ArrowRightIcon } from "@/components/icons/navigation-icons";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { fadeIn } from "@/animations/variants";
import { SectionHeader } from "@/features/landing/components/section-header";
import { useMockDemo, type DemoPhase } from "@/features/landing/hooks/use-mock-demo";
import { DEMO_PROMPTS } from "@/features/landing/data/features";
import { SECTION_LABELS } from "@/features/landing/constants/landing";

// ---------------------------------------------------------------------------
// Phase label + color
// ---------------------------------------------------------------------------

const PHASE_CONFIG: Record<DemoPhase, { label: string; color: string }> = {
  idle: { label: "Ready", color: "text-muted-foreground" },
  typing: { label: "Typing...", color: "text-primary" },
  planning: { label: "Planning...", color: "text-accent" },
  searching: { label: "Searching codebase...", color: "text-warning" },
  building: { label: "Building context...", color: "text-accent" },
  answering: { label: "Generating answer...", color: "text-success" },
  done: { label: "Complete", color: "text-success" },
};

// ---------------------------------------------------------------------------
// Markdown-lite renderer (bold only)
// ---------------------------------------------------------------------------

function renderMarkdown(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-foreground">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function MockDemoSection() {
  const prefersReduced = useReducedMotion();
  const { state, start, reset } = useMockDemo();
  const [activePrompt, setActivePrompt] = useState<string | null>(null);

  const handlePromptClick = (prompt: string) => {
    setActivePrompt(prompt);
    start(prompt);
  };

  const handleReset = () => {
    setActivePrompt(null);
    reset();
  };

  const phaseConfig = PHASE_CONFIG[state.phase];
  const isRunning = state.phase !== "idle" && state.phase !== "done";

  return (
    <section
      id="demo"
      aria-labelledby="demo-heading"
      className="section-padding"
    >
      <div className="content-width">
        <SectionHeader
          badge="Live Demo"
          title={SECTION_LABELS.demo}
          subtitle={SECTION_LABELS.demoSubtitle}
          headingId="demo-heading"
        />

        {/* Demo interface */}
        <motion.div
          variants={prefersReduced ? {} : fadeIn}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="mx-auto max-w-3xl"
        >
          <div className="overflow-hidden rounded-2xl border border-border bg-surface/60 shadow-card backdrop-blur-sm">
            {/* Terminal header */}
            <div className="flex items-center justify-between border-b border-border bg-muted/20 px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5" aria-hidden="true">
                  <div className="h-2.5 w-2.5 rounded-full bg-danger/60" />
                  <div className="h-2.5 w-2.5 rounded-full bg-warning/60" />
                  <div className="h-2.5 w-2.5 rounded-full bg-success/60" />
                </div>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <TerminalIcon size={12} aria-hidden="true" />
                  <span>RepoMind Query Interface</span>
                </div>
              </div>

              {/* Phase status */}
              <div role="status" aria-live="polite" aria-label={`Status: ${phaseConfig.label}`}>
                <span className={cn("text-xs font-medium", phaseConfig.color)}>
                  {isRunning && (
                    <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-current" aria-hidden="true" />
                  )}
                  {phaseConfig.label}
                </span>
              </div>
            </div>

            {/* Query prompt chips */}
            {state.phase === "idle" && (
              <div className="border-b border-border/50 p-4">
                <p className="mb-3 text-xs font-medium text-muted-foreground">
                  Try a sample question:
                </p>
                <div className="flex flex-wrap gap-2">
                  {DEMO_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => handlePromptClick(prompt)}
                      className={cn(
                        "focus-ring rounded-lg border border-border/60 bg-card/50 px-3 py-1.5",
                        "text-xs font-medium text-muted-foreground transition-all duration-150",
                        "hover:border-primary/30 hover:bg-primary/5 hover:text-primary",
                        activePrompt === prompt && "border-primary/30 bg-primary/5 text-primary",
                      )}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Query display */}
            <div className="min-h-[64px] border-b border-border/50 p-4">
              <div className="flex items-start gap-2">
                <span className="mt-0.5 text-xs font-mono font-semibold text-primary">
                  &gt;
                </span>
                <span
                  className={cn(
                    "font-mono text-sm text-foreground",
                    state.phase === "typing" && "cursor-blink",
                  )}
                  aria-live="polite"
                  aria-label={`Query: ${state.displayedQuery || "Enter a question above"}`}
                >
                  {state.displayedQuery || (
                    <span className="text-muted-foreground">
                      Click a question above to begin...
                    </span>
                  )}
                </span>
              </div>
            </div>

            {/* Search results */}
            <AnimatePresence>
              {(state.phase === "searching" || state.phase === "building" || state.phase === "answering" || state.phase === "done") && state.searchResults.length > 0 && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  className="border-b border-border/50 p-4"
                  aria-live="polite"
                  aria-label="Search results"
                >
                  <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-accent">
                    <FileSearchIcon size={12} aria-hidden="true" />
                    Relevant chunks found
                  </div>
                  <ul className="space-y-1">
                    {state.searchResults.map((result, i) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.2 }}
                        className="flex items-center gap-2 text-xs"
                      >
                        <span className="font-mono text-muted-foreground">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <code className="text-foreground">{result}</code>
                      </motion.li>
                    ))}
                  </ul>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Context files */}
            <AnimatePresence>
              {(state.phase === "building" || state.phase === "answering" || state.phase === "done") && state.contextFiles.length > 0 && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  className="border-b border-border/50 p-4"
                  aria-live="polite"
                  aria-label="Context files"
                >
                  <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-primary">
                    <SparklesIcon size={12} aria-hidden="true" />
                    Context assembled
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {state.contextFiles.map((file, i) => (
                      <motion.span
                        key={i}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="rounded-md bg-primary/10 px-2 py-0.5 font-mono text-[10px] text-primary"
                      >
                        {file}
                      </motion.span>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Answer */}
            <AnimatePresence>
              {(state.phase === "answering" || state.phase === "done") && state.displayedAnswer && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-4"
                  aria-live="polite"
                  aria-label="Generated answer"
                >
                  <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-success">
                    <SparklesIcon size={12} aria-hidden="true" />
                    RepoMind
                  </div>
                  <div
                    className={cn(
                      "whitespace-pre-wrap text-sm leading-relaxed text-foreground",
                      state.phase === "answering" && "cursor-blink",
                    )}
                  >
                    {renderMarkdown(state.displayedAnswer)}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Done — reset button */}
            <AnimatePresence>
              {state.phase === "done" && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="border-t border-border/50 p-4"
                >
                  <Button
                    variant="ghost"
                    onClick={handleReset}
                    aria-label="Ask another question — reset the demo"
                    className="gap-2 text-xs"
                  >
                    Ask another question
                    <ArrowRightIcon size={12} aria-hidden="true" />
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Disclaimer */}
          <p className="mt-4 text-center text-xs text-muted-foreground">
            This is a scripted demo. No backend required.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
