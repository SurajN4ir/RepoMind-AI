"use client";

/**
 * features/landing/sections/tech-stack-section.tsx
 *
 * Technology stack showcase.
 *
 * Technologies are grouped by category (Backend, AI/ML, Frontend, Infra)
 * and displayed as badge grids. Each category reveals on scroll with stagger.
 * Data-driven from tech-stack.ts.
 */

import { motion, useReducedMotion } from "motion/react";
import { cn } from "@/lib/utils";
import { staggerContainer, staggerItem } from "@/animations/variants";
import { SectionHeader } from "@/features/landing/components/section-header";
import {
  TECH_STACK,
  TECH_CATEGORIES,
  CATEGORY_LABELS,
  CATEGORY_COLORS,
} from "@/features/landing/data/tech-stack";
import { SECTION_LABELS } from "@/features/landing/constants/landing";

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

export function TechStackSection() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      id="tech"
      aria-labelledby="tech-heading"
      className="section-padding"
    >
      <div className="content-width">
        <SectionHeader
          badge="Technology"
          title={SECTION_LABELS.tech}
          subtitle={SECTION_LABELS.techSubtitle}
          headingId="tech-heading"
        />

        {/* Category groups */}
        <div className="grid gap-8 sm:grid-cols-2">
          {TECH_CATEGORIES.map((category) => {
            const items = TECH_STACK.filter((t) => t.category === category);
            return (
              <motion.div
                key={category}
                variants={prefersReduced ? {} : staggerContainer}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.2 }}
                className="rounded-2xl border border-border bg-surface/40 p-6"
              >
                {/* Category label */}
                <motion.div
                  variants={prefersReduced ? {} : staggerItem}
                  className="mb-4 flex items-center gap-2"
                >
                  <span
                    className={cn(
                      "rounded-full border px-2.5 py-0.5 text-xs font-semibold",
                      CATEGORY_COLORS[category],
                    )}
                  >
                    {CATEGORY_LABELS[category]}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {items.length} technologies
                  </span>
                </motion.div>

                {/* Tech badges */}
                <div className="flex flex-wrap gap-2">
                  {items.map((tech) => (
                    <motion.div
                      key={tech.id}
                      variants={prefersReduced ? {} : staggerItem}
                    >
                      <div
                        title={tech.description}
                        className={cn(
                          "group relative cursor-default rounded-lg border px-3 py-1.5",
                          "text-xs font-medium transition-all duration-150",
                          "hover:scale-105 hover:shadow-sm",
                          CATEGORY_COLORS[category],
                        )}
                        role="listitem"
                      >
                        {tech.name}
                        {/* Tooltip */}
                        <span
                          role="tooltip"
                          className={cn(
                            "pointer-events-none absolute -top-9 left-1/2 z-10",
                            "-translate-x-1/2 whitespace-nowrap rounded-lg border border-border",
                            "bg-card px-2 py-1 text-[10px] text-muted-foreground shadow-card",
                            "opacity-0 transition-opacity group-hover:opacity-100",
                          )}
                        >
                          {tech.description}
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
