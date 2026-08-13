"use client";

/**
 * features/landing/sections/pipeline-section.tsx
 *
 * Animated Repository Intelligence Pipeline.
 *
 * The pipeline nodes and connectors are rendered as a horizontal scrollable
 * list on mobile and a full-width visual on desktop.
 *
 * Anime.js animation is loaded dynamically (lazy) and fires once when
 * the section enters the viewport via IntersectionObserver.
 *
 * Animation sequence (see animations/pipeline.ts):
 * 1. Node wrappers fade + scale in with stagger
 * 2. Node icons pop in with easeOutBack
 * 3. SVG connector lines draw from left to right
 * 4. Terminal node glows with a pulse
 *
 * Accessible:
 * - section has role="region" and aria-label
 * - Pipeline has role="list" / role="listitem"
 * - Decorative SVGs are aria-hidden
 */

import { useEffect, useRef } from "react";
import { useReducedMotion } from "motion/react";

import { PipelineIcon } from "@/components/icons/pipeline-icons";
import { cn } from "@/lib/utils";
import { SectionHeader } from "@/features/landing/components/section-header";
import { useInView } from "@/animations/scroll";
import { runPipelineAnimation, startTerminalPulse } from "@/animations/pipeline";
import {
  PIPELINE_NODES,
  PHASE_BG,
  PHASE_ICON_COLOR,
} from "@/features/landing/data/pipeline";
import { SECTION_LABELS } from "@/features/landing/constants/landing";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function PipelineSection() {
  const prefersReduced = useReducedMotion();
  const [sectionRef, isInView] = useInView<HTMLElement>({ threshold: 0.2 });
  const animationCleanupRef = useRef<(() => void) | null>(null);
  const pulseCleanupRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!isInView || prefersReduced) return;

    const cleanupAnim = runPipelineAnimation();
    animationCleanupRef.current = cleanupAnim;

    // Start terminal pulse after the main animation settles
    const pulseTimeout = setTimeout(() => {
      const cleanup = startTerminalPulse(".pipeline-node-terminal");
      pulseCleanupRef.current = cleanup;
    }, PIPELINE_NODES.length * 130 + 900);

    return () => {
      cleanupAnim();
      clearTimeout(pulseTimeout);
      pulseCleanupRef.current?.();
    };
  }, [isInView, prefersReduced]);

  return (
    <section
      ref={sectionRef}
      id="pipeline"
      aria-label={SECTION_LABELS.pipeline}
      className="section-padding"
    >
      <div className="content-width">
        <SectionHeader
          badgeEl={
            <span className="mb-4 inline-block rounded-full border border-primary/20 bg-primary/8 px-3 py-1 text-xs font-medium text-primary">
              Intelligence Pipeline
            </span>
          }
          title={
            <>
              From Code to{" "}
              <span className="text-gradient">Grounded Answer</span>
            </>
          }
          subtitle={SECTION_LABELS.pipelineSubtitle}
          viewportAmount={0.3}
        />

        {/* Pipeline visual */}
        <div
          role="img"
          aria-label={`Pipeline: ${PIPELINE_NODES.map((n) => n.label).join(" → ")}`}
          className="relative"
        >
          {/* SVG connectors — desktop only (aria-hidden) */}
          <svg
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 hidden h-full w-full md:block"
            preserveAspectRatio="none"
          >
            {PIPELINE_NODES.slice(0, -1).map((_, i) => {
              const totalNodes = PIPELINE_NODES.length;
              const pct = (100 / totalNodes);
              const x1H = (pct * i + pct / 2) + pct / 2 + "%";
              const x2H = (pct * (i + 1) + pct / 2) - pct / 2 + "%";
              return (
                <line
                  key={i}
                  className="pipeline-connector"
                  x1={x1H}
                  y1="50%"
                  x2={x2H}
                  y2="50%"
                  stroke="hsl(var(--border))"
                  strokeWidth="1.5"
                  strokeDasharray="4 3"
                />
              );
            })}
          </svg>

          {/* Nodes */}
          <div className="relative grid grid-cols-2 gap-4 sm:grid-cols-4 md:grid-cols-8">
            {PIPELINE_NODES.map((node, i) => {
              const isTerminal = i === PIPELINE_NODES.length - 1;
              return (
                <div
                  key={node.id}
                  role="listitem"
                  className={cn(
                    "pipeline-node group relative flex flex-col items-center gap-3 rounded-2xl border p-4 transition-shadow duration-300",
                    PHASE_BG[node.phase],
                    isTerminal && "pipeline-node-terminal",
                    // Fade in state (anime.js will override)
                    !prefersReduced && "opacity-0",
                  )}
                  title={node.description}
                >
                  {/* Icon */}
                  <div
                    className={cn(
                      "pipeline-node-icon flex h-10 w-10 items-center justify-center rounded-xl",
                      PHASE_BG[node.phase],
                      !prefersReduced && "opacity-0",
                    )}
                    aria-hidden="true"
                  >
                    <PipelineIcon
                      name={node.icon}
                      size={20}
                      className={PHASE_ICON_COLOR[node.phase]}
                    />
                  </div>

                  {/* Glow effect (terminal node) */}
                  {isTerminal && (
                    <div
                      className="pipeline-node-glow absolute inset-0 rounded-2xl opacity-0"
                      aria-hidden="true"
                    />
                  )}

                  {/* Label */}
                  <span className="text-center text-xs font-semibold text-foreground">
                    {node.label}
                  </span>

                  {/* Step number */}
                  <span className="text-[10px] font-mono text-muted-foreground">
                    {String(i + 1).padStart(2, "0")}
                  </span>

                  {/* Tooltip on hover */}
                  <div
                    role="tooltip"
                    className={cn(
                      "pointer-events-none absolute -bottom-2 left-1/2 z-10 w-40 -translate-x-1/2 translate-y-full",
                      "rounded-xl border border-border bg-card px-3 py-2 text-xs text-muted-foreground",
                      "opacity-0 shadow-card transition-opacity duration-200 group-hover:opacity-100",
                    )}
                  >
                    {node.description}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Mobile arrow chain */}
        <p className="mt-8 text-center text-xs text-muted-foreground md:hidden">
          {PIPELINE_NODES.map((n) => n.label).join(" → ")}
        </p>
      </div>
    </section>
  );
}
