"use client";

/**
 * features/landing/sections/why-section.tsx
 *
 * "Why RepoMind" — comparison table between Traditional RAG and RepoMind.
 *
 * Rows reveal with stagger animation on scroll entry.
 * Check / cross icons animate in per-row.
 * Data-driven from comparison.ts.
 */

import { motion, useReducedMotion } from "motion/react";
import { CheckIcon, CrossIcon } from "@/components/icons/feature-icons";
import { cn } from "@/lib/utils";
import { staggerContainer, staggerItem } from "@/animations/variants";
import { SectionHeader } from "@/features/landing/components/section-header";
import { COMPARISON_ROWS } from "@/features/landing/data/comparison";
import { SECTION_LABELS } from "@/features/landing/constants/landing";

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

export function WhySection() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      id="why"
      aria-labelledby="why-heading"
      className="section-padding"
    >
      <div className="content-width">
        <SectionHeader
          badge="Why RepoMind"
          title={SECTION_LABELS.why}
          subtitle={SECTION_LABELS.whySubtitle}
          headingId="why-heading"
        />

        {/* Comparison table */}
        <div className="overflow-hidden rounded-2xl border border-border">
          {/* Table header */}
          <div className="hidden sm:grid sm:grid-cols-[1.2fr_1fr_1fr] border-b border-border bg-surface/80">
            <div className="px-6 py-4 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Dimension
            </div>
            <div className="border-l border-border px-6 py-4">
              <span className="inline-flex items-center gap-2 text-xs font-semibold text-danger/80">
                <CrossIcon size={14} aria-hidden="true" />
                Traditional RAG
              </span>
            </div>
            <div className="border-l border-border px-6 py-4">
              <span className="inline-flex items-center gap-2 text-xs font-semibold text-success">
                <CheckIcon size={14} aria-hidden="true" />
                RepoMind
              </span>
            </div>
          </div>

          {/* Rows */}
          <motion.div
            variants={prefersReduced ? {} : staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
          >
            {COMPARISON_ROWS.map((row, i) => (
              <motion.div
                key={row.id}
                variants={prefersReduced ? {} : staggerItem}
                className={cn(
                  "flex flex-col sm:grid sm:grid-cols-[1.2fr_1fr_1fr] border-b border-border/50 last:border-0",
                  i % 2 === 0 ? "bg-transparent" : "bg-surface/30",
                )}
              >
                {/* Dimension */}
                <div className="px-6 py-4 sm:py-5">
                  <span className="text-sm font-semibold text-foreground">{row.dimension}</span>
                </div>

                {/* Traditional */}
                <div className="flex items-start gap-2 border-t border-border/30 px-6 py-3 sm:border-l sm:border-t-0 sm:py-5">
                  <CrossIcon
                    size={14}
                    className="mt-0.5 flex-shrink-0 text-danger/60"
                    aria-label="Disadvantage"
                  />
                  <span className="text-sm text-muted-foreground">{row.traditional}</span>
                </div>

                {/* RepoMind */}
                <div className="flex items-start gap-2 border-t border-border/30 px-6 py-3 sm:border-l sm:border-t-0 sm:py-5">
                  <CheckIcon
                    size={14}
                    className="mt-0.5 flex-shrink-0 text-success"
                    aria-label="Advantage"
                  />
                  <span className="text-sm font-medium text-foreground">{row.repoMind}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
