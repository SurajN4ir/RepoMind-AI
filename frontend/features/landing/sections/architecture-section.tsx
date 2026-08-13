"use client";

/**
 * features/landing/sections/architecture-section.tsx
 *
 * Architecture overview section showing two pipeline rows:
 *
 * Row 1 (Ingestion): Repository → Ingest → Parse → Chunk → Embed → Index
 * Row 2 (Query):     UserRequest → Query Engine → Retrieve → Context → Orchestrate → Respond
 *
 * Each step is a pill with an icon, label, and phase color.
 * Steps are connected by animated arrows.
 * Staggered scroll-reveal via Framer Motion.
 */

import { motion, useReducedMotion } from "motion/react";
import { ArrowRightIcon } from "@/components/icons/navigation-icons";
import { cn } from "@/lib/utils";
import { staggerContainer, staggerItem } from "@/animations/variants";
import { SectionHeader } from "@/features/landing/components/section-header";
import { SECTION_LABELS } from "@/features/landing/constants/landing";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ArchStep {
  label: string;
  sublabel: string;
  color: string;
  bg: string;
}

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

const INGESTION_PIPELINE: ArchStep[] = [
  { label: "Repository", sublabel: "Source", color: "text-primary", bg: "bg-primary/10 border-primary/20" },
  { label: "Ingest", sublabel: "Clone", color: "text-primary", bg: "bg-primary/10 border-primary/20" },
  { label: "Parse", sublabel: "Tree-sitter", color: "text-accent", bg: "bg-accent/10 border-accent/20" },
  { label: "Chunk", sublabel: "Semantic", color: "text-accent", bg: "bg-accent/10 border-accent/20" },
  { label: "Embed", sublabel: "Vectors", color: "text-accent", bg: "bg-accent/10 border-accent/20" },
  { label: "Index", sublabel: "pgvector", color: "text-success", bg: "bg-success/10 border-success/20" },
];

const QUERY_PIPELINE: ArchStep[] = [
  { label: "User Request", sublabel: "Natural Language", color: "text-warning", bg: "bg-warning/10 border-warning/20" },
  { label: "Query Engine", sublabel: "Parse Intent", color: "text-warning", bg: "bg-warning/10 border-warning/20" },
  { label: "Retrieve", sublabel: "Semantic Search", color: "text-accent", bg: "bg-accent/10 border-accent/20" },
  { label: "Context", sublabel: "Builder", color: "text-accent", bg: "bg-accent/10 border-accent/20" },
  { label: "Orchestrate", sublabel: "AI Composer", color: "text-primary", bg: "bg-primary/10 border-primary/20" },
  { label: "Response", sublabel: "Cited Answer", color: "text-success", bg: "bg-success/10 border-success/20" },
];

// ---------------------------------------------------------------------------
// Pipeline Row
// ---------------------------------------------------------------------------

interface PipelineRowProps {
  label: string;
  steps: ArchStep[];
  prefersReduced: boolean | null;
}

function PipelineRow({ label, steps, prefersReduced }: PipelineRowProps) {
  return (
    <div className="mb-8">
      <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
        {label}
      </p>
      <div className="flex flex-wrap items-center gap-2">
        {steps.map((step, i) => (
          <div key={step.label} className="flex items-center gap-2">
            <motion.div
              variants={prefersReduced ? {} : staggerItem}
              className={cn(
                "flex flex-col items-center justify-center rounded-xl border px-3 py-2.5 text-center",
                step.bg,
              )}
            >
              <span className={cn("text-xs font-semibold", step.color)}>{step.label}</span>
              <span className="mt-0.5 text-[10px] text-muted-foreground">{step.sublabel}</span>
            </motion.div>
            {i < steps.length - 1 && (
              <ArrowRightIcon
                size={14}
                className="flex-shrink-0 text-border"
                aria-hidden="true"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

export function ArchitectureSection() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      id="architecture"
      aria-labelledby="arch-heading"
      className="section-padding"
    >
      <div className="content-width">
        <SectionHeader
          badge="Architecture"
          title={SECTION_LABELS.architecture}
          subtitle={SECTION_LABELS.architectureSubtitle}
          headingId="arch-heading"
        />

        {/* Architecture visual */}
        <motion.div
          className="rounded-2xl border border-border bg-surface/60 p-8 backdrop-blur-sm"
          variants={prefersReduced ? {} : staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.15 }}
        >
          <PipelineRow
            label="Ingestion Pipeline"
            steps={INGESTION_PIPELINE}
            prefersReduced={prefersReduced}
          />

          {/* Divider */}
          <div className="my-6 border-t border-border/60" />

          <PipelineRow
            label="Query Pipeline"
            steps={QUERY_PIPELINE}
            prefersReduced={prefersReduced}
          />

          {/* Legend */}
          <div className="mt-6 flex flex-wrap gap-4 border-t border-border/40 pt-6">
            {[
              { label: "Ingestion", color: "bg-primary/20 text-primary" },
              { label: "Processing", color: "bg-accent/20 text-accent" },
              { label: "Storage", color: "bg-success/20 text-success" },
              { label: "Query", color: "bg-warning/20 text-warning" },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-2">
                <div className={cn("h-2 w-2 rounded-full", item.color)} aria-hidden="true" />
                <span className="text-xs text-muted-foreground">{item.label}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
