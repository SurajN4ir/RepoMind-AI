"use client";

/**
 * features/landing/sections/features-section.tsx
 *
 * Interactive feature showcase — 6 cards in a responsive grid.
 * Featured (core) cards are visually elevated.
 * Cards reveal with a stagger animation on scroll entry.
 * Hover reveals a directional arrow with a spring transition.
 */

import { motion, useReducedMotion } from "motion/react";
import { ArrowRightIcon } from "@/components/icons/navigation-icons";
import {
  SemanticSearchIcon,
  AIQAIcon,
  CodeChunkingIcon,
  SmartIndexingIcon,
  ContextBuildingIcon,
  MultiRepoIcon,
} from "@/components/icons/feature-icons";
import { cn } from "@/lib/utils";
import { staggerContainer, staggerItem, iconHover } from "@/animations/variants";
import { SectionHeader } from "@/features/landing/components/section-header";
import { FEATURES } from "@/features/landing/data/features";
import { SECTION_LABELS } from "@/features/landing/constants/landing";
import type { LucideProps } from "lucide-react";

// ---------------------------------------------------------------------------
// Icon resolver (keeps feature-icons layer as source of truth)
// ---------------------------------------------------------------------------

const ICON_MAP: Record<string, React.ComponentType<LucideProps>> = {
  SemanticSearchIcon,
  AIQAIcon,
  CodeChunkingIcon,
  SmartIndexingIcon,
  ContextBuildingIcon,
  MultiRepoIcon,
};

// ---------------------------------------------------------------------------
// Feature Card
// ---------------------------------------------------------------------------

interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
  badge?: string;
  featured?: boolean;
}

function FeatureCard({ title, description, icon, badge, featured }: FeatureCardProps) {
  const Icon = ICON_MAP[icon] ?? SemanticSearchIcon;
  const prefersReduced = useReducedMotion();

  return (
    <motion.article
      variants={prefersReduced ? {} : staggerItem}
      initial="rest"
      whileHover={prefersReduced ? undefined : "hover"}
      className={cn(
        "group relative flex flex-col gap-4 rounded-2xl border p-6 transition-all duration-200",
        featured
          ? "border-primary/20 bg-primary/5 shadow-glow"
          : "border-border bg-surface/60 hover:border-border/80 hover:bg-surface/80",
      )}
    >
      {/* Featured highlight */}
      {featured && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent"
        />
      )}

      {/* Icon */}
      <motion.div
        variants={prefersReduced ? {} : iconHover}
        className={cn(
          "flex h-10 w-10 items-center justify-center rounded-xl",
          featured ? "bg-primary/15 text-primary" : "bg-muted text-muted-foreground group-hover:text-foreground",
        )}
        aria-hidden="true"
      >
        <Icon size={20} />
      </motion.div>

      {/* Content */}
      <div className="flex flex-1 flex-col gap-2">
        {badge && (
          <span className="w-fit rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            {badge}
          </span>
        )}
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
        <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
      </div>

      {/* Hover arrow */}
      <div
        className="flex items-center gap-1 text-xs font-medium text-primary opacity-0 transition-opacity duration-200 group-hover:opacity-100"
        aria-hidden="true"
      >
        Learn more
        <ArrowRightIcon size={12} className="transition-transform duration-200 group-hover:translate-x-0.5" />
      </div>
    </motion.article>
  );
}

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

export function FeaturesSection() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      id="features"
      aria-labelledby="features-heading"
      className="section-padding"
    >
      <div className="content-width">
        <SectionHeader
          badge="Features"
          title={SECTION_LABELS.features}
          subtitle={SECTION_LABELS.featuresSubtitle}
          headingId="features-heading"
        />

        {/* Card grid */}
        <motion.div
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
          variants={prefersReduced ? {} : staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
        >
          {FEATURES.map((feature) => (
            <FeatureCard key={feature.id} {...feature} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
